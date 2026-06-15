from __future__ import annotations
import sys
import os
from parser import Parser
from pathfinder import Pathfinder
from simulator import Simulator
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'srcs'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'visualizer'))


def main() -> None:
    """Entry point for the fly_in drone routing simulation."""

    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)

    file_path: Path = Path(sys.argv[1])

    parser: Parser = Parser(file_path)
    graph = parser.parse()
    nb_drones: int = parser.nb_drones
    pathfinder: Pathfinder = Pathfinder(graph)
    simulator: Simulator = Simulator(graph, nb_drones, pathfinder)
    simulator.create_drone()
    simulator.run_simulator()
    simulator.print_output()

    try:
        from visualizer import Visualizer
        visualizer: Visualizer = Visualizer(graph, simulator.history)
        visualizer.rotate_pygame()
    except Exception:
        pass


if __name__ == "__main__":
    main()
