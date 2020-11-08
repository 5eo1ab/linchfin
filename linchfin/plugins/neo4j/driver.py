from neo4j import GraphDatabase
from linchfin.metadata import STOCK_SECTORS
from linchfin.base.dataclasses.entities import Asset, AssetClass, Cluster
from linchfin.core.clustering.sectors import SectorTree
import re


class GraphManager:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def __del__(self):
        self.driver.close()

    def create(self, graph, parent=None):
        if isinstance(graph, Cluster):
            node_name = re.sub(pattern='[\s\-&,]', repl='_', string=graph.name)

            if parent is None:
                self.create_node(graph=graph, node_name=node_name)

            for e in graph.elements:
                node_name = re.sub(pattern='[\s\-&,]', repl='_', string=e.name)
                if isinstance(e, Cluster):
                    self.create_node(graph=e, node_name=node_name)
                    self.create(graph=e, parent=graph)
                    self.create_link(from_node=graph, to_node=e)
                elif isinstance(e, Asset):
                    self.create_node(graph=e, node_name=node_name)
                    self.create_link(from_node=graph, to_node=e)
                else:
                    raise RuntimeError("unsupported graph type")

    def get_node_type(self, graph):
        if isinstance(graph, Cluster):
            node_type = "Cluster"
        elif isinstance(graph, Asset):
            node_type = "Asset"
        else:
            raise RuntimeError("unsupported node type")
        return node_type

    def create_node(self, graph: Cluster or Asset, node_name):
        node_type = self.get_node_type(graph=graph)
        create_query = f"""CREATE ({node_name}:{node_type} {{name: '{graph.name}'}})"""

        with self.driver.session() as sess:
             sess.run(query=create_query)

    def create_link(self, from_node: Cluster or Asset, to_node: Cluster or Asset):
        create_query = \
            f"""MATCH (a), (b) WHERE a.name='{from_node.name}' AND b.name = '{to_node.name}'
            CREATE (a)-[r:HAS]->(b)
            RETURN r
            """

        with self.driver.session() as sess:
             sess.run(query=create_query)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]


if __name__ == "__main__":
    greeter = GraphManager("bolt://localhost:7687", "neo4j", "pass")
    sector_graph = SectorTree(STOCK_SECTORS)
    greeter.create(graph=sector_graph.root)
    del greeter
