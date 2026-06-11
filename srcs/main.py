from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'srcs'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'visualizer'))


from parser import Parser
from pathfinder import Pathfinder
from simulator import Simulator
from visualizer import Visualizer

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

    visualizer = Visualizer(graph, simulator.history)
    visualizer.rotate_pygame()



if __name__ == "__main__":
    main()
