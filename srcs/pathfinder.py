from parser
from graph import Graph


class Pathfinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_path