from __future__ import annotations
import sys
import os
from parser import Parser
from pathfinder import Pathfinder
from simulator import Simulator


def main() -> None:
    file_path = sys.argv[1]
    parser = Parser(file_path)
    graph = parser.parse()
    nb_drones = parser.nb_drones
    pathfinder = Pathfinder(graph)
    simulator = Simulator(graph, nb_drones, pathfinder)
    simulator.create_drone()
    simulator.run_simulator()
    simulator.print_output()


if __name__ == "__main__":
    main()
