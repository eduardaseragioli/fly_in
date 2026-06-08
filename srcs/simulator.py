from __future__ import annotations
from graph import Graph
from pathfinder import Pathfinder
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
        for i in range(1, self.nb_drones + 1):
            drone_id = f"D{i}"
            drone = Drone(drone_id, self.graph.start_zone, self.graph.end_zone)
            self.drones.append(drone)

    def run_simulator(self) -> None:
        while not all(drone.status == Status.arrived for drone in self.drones):
            turn_movements: list[str] = []
            moved_this_turn: set = set()
            completed_transit_this_turn: set = set()

            for drone in self.drones:
                if drone.status == Status.transit_to_restricted:
                    if drone.turn_destination == self.current_turn:
                        if drone.current_connection is not None:
                            drone.current_connection.remove_drone(drone)
                        if drone.transit_destination_zone is not None:
                            drone.transit_destination_zone.drone_actual.append(
                                drone)
                            drone.current_zone = drone.transit_destination_zone
                            turn_movements.append(
                                f"{drone.id_drone}-{drone.transit_destination_zone.name}")
                        if drone.planned_route:
                            drone.planned_route.pop(0)
                        if drone.transit_destination_zone == drone.destination_zone:
                            drone.status = Status.arrived
                            drone.transit_destination_zone.remove_drone(drone)
                        else:
                            drone.status = Status.in_motion
                        drone.transit_destination_zone = None
                        drone.current_connection = None
                        completed_transit_this_turn.add(drone.id_drone)

            for drone in self.drones:
                if drone.status != Status.arrived and drone.status != Status.transit_to_restricted:
                    if not drone.planned_route:
                        drone.planned_route = self.pathfinder.find_path(
                            drone.current_zone, drone.destination_zone)
                    if drone.planned_route:
                        next_zone = drone.planned_route[0]
                        connection = self.graph.get_connection(
                            drone.current_zone, next_zone)
                        if connection and not connection.has_capacity():
                            continue
                        if drone.id_drone in moved_this_turn:
                            continue
                        if drone.id_drone in completed_transit_this_turn:
                            continue
                        if next_zone.type_zone == Type_zone.restricted:
                            if drone.start_transit_restricted(next_zone, self.current_turn, connection):
                                turn_movements.append(
                                    f"{drone.id_drone}-{connection.name}")
                        else:
                            if drone.move_drone(next_zone):
                                turn_movements.append(
                                    f"{drone.id_drone}-{next_zone.name}")
            if turn_movements:
                self.history.append(" ".join(turn_movements))

            self.current_turn += 1

    def print_output(self) -> None:
        for line in self.history:
            print(line)
        print(f"Total turns: {self.current_turn}")

    def get_turns(self) -> int:
        return self.current_turn
