from __future__ import annotations
from graph import Graph
from pathfinder import Pathfinder, ReservationTable
from drone import Drone, Status
from zones import Zone, Type_zone


class Simulator:
    def __init__(self, graph: Graph, nb_drones: int, pathfinder: Pathfinder) -> None:
        self.graph = graph
        self.pathfinder = pathfinder
        self.current_turn: int = 0
        self.history: list[str] = []
        self.drones: list[Drone] = []
        self.nb_drones = nb_drones

    def create_drone(self) -> None:
        table = ReservationTable()

        for i in range(1, self.nb_drones + 1):
            drone_id = f"D{i}"
            drone = Drone(drone_id, self.graph.start_zone, self.graph.end_zone)

            path = self.pathfinder.find_path_with_reservations(
                self.graph.start_zone, self.graph.end_zone,
                table, start_turn=0)

            if not path:
                self.drones.append(drone)
                continue

            # Registrar reservas
            for idx, (zone, turn) in enumerate(path):
                table.reserve_zone(zone.name, turn)
                if idx < len(path) - 1:
                    next_zone, _ = path[idx + 1]
                    if next_zone != zone:
                        conn = self.graph.get_connection(zone, next_zone)
                        if conn:
                            table.reserve_edge(zone.name, next_zone.name, turn)

            # planned_path: lista de (zona, turno) sem o start
            drone.planned_path = [(z, t) for z, t in path if z != self.graph.start_zone]
            drone.path_index = 0
            drone.start_turn = 0
            self.drones.append(drone)

    def run_simulator(self) -> None:
        delivered: set[str] = set()
        self.current_turn = 0
        max_turns = 1000

        while len(delivered) < len(self.drones) and self.current_turn < max_turns:
            self.current_turn += 1
            movements: list[str] = []

            for drone in self.drones:
                if drone.status == Status.arrived:
                    continue

                path = getattr(drone, 'planned_path', [])
                if not path:
                    drone.status = Status.arrived
                    delivered.add(drone.id_drone)
                    continue

                # Avançar índice para o turno atual
                while (drone.path_index < len(path) and
                       path[drone.path_index][1] < self.current_turn):
                    drone.path_index += 1

                if drone.path_index >= len(path):
                    drone.status = Status.arrived
                    delivered.add(drone.id_drone)
                    continue

                zone, target_turn = path[drone.path_index]

                if target_turn == self.current_turn:
                    if zone != drone.current_zone:
                        movements.append(f"{drone.id_drone}-{zone.name}")
                        drone.current_zone = zone

                    if zone == self.graph.end_zone:
                        drone.status = Status.arrived
                        delivered.add(drone.id_drone)

                    drone.path_index += 1

            if movements:
                self.history.append(" ".join(movements))

    def print_output(self) -> None:
        for line in self.history:
            print(line)
        print(f"Total turns: {self.current_turn}")

    def get_turns(self) -> int:
        return self.current_turn
    