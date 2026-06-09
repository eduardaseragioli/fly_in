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

        paths = self.pathfinder.find_k_paths(
            self.graph.start_zone,
            self.graph.end_zone,
            10
        )

        self.routes = [Route(path) for path in paths]

    def create_drone(self) -> None:
        for i in range(1, self.nb_drones + 1):
            drone_id = f"D{i}"
            drone = Drone(drone_id, self.graph.start_zone, self.graph.end_zone)

            best_route = min(self.routes, key=lambda route: route.score())

            # Remove o nó inicial pois o drone já começa lá
            route_copy = best_route.path.copy()
            if route_copy and route_copy[0] == self.graph.start_zone:
                route_copy.pop(0)
            drone.planned_route = route_copy
            best_route.assigned_drones += 1

            self.drones.append(drone)

    def run_simulator(self) -> None:
        paths = self.pathfinder.find_k_paths(
            self.graph.start_zone, self.graph.end_zone, 3)
        for i, p in enumerate(paths):
            print(f"Path {i}: {[z.name for z in p]}")

        max_turns = 1000
        while (not all(drone.status == Status.arrived
                       for drone in self.drones) and
               self.current_turn < max_turns):
            turn_movements: list[str] = []
            moved_this_turn: set = set()
            completed_transit_this_turn: set = set()

            # Processar drones em transit_to_restricted
            for drone in self.drones:
                if drone.status == Status.transit_to_restricted:
                    if drone.turn_destination == self.current_turn:
                        if drone.current_connection is not None:
                            drone.current_connection.remove_drone(drone)
                        if drone.transit_destination_zone is not None:
                            drone.transit_destination_zone.add_drone(drone)
                            drone.current_zone = drone.transit_destination_zone
                            dest_name = drone.transit_destination_zone.name
                            turn_movements.append(
                                f"{drone.id_drone}-{dest_name}")
                        
                        if drone.planned_route:
                            drone.planned_route.pop(0)
                        
                        if (drone.transit_destination_zone ==
                                drone.destination_zone):
                            drone.status = Status.arrived
                        else:
                            drone.status = Status.in_motion
                        
                        drone.transit_destination_zone = None
                        drone.current_connection = None
                        completed_transit_this_turn.add(drone.id_drone)

            # Processar movimentos de drones stopped/in_motion
            for drone in self.drones:
                if drone.status == Status.arrived:
                    continue
                if drone.id_drone in completed_transit_this_turn:
                    continue
                if drone.id_drone in moved_this_turn:
                    continue
                
                if not drone.planned_route:
                    continue
                
                next_zone = drone.planned_route[0]
                
                if drone.current_zone is None or next_zone is None:
                    continue
                
                connection = self.graph.get_connection(
                    drone.current_zone, next_zone)
                
                if connection is None:
                    continue
                if not connection.has_capacity():
                    continue
                if not next_zone.has_capacity():
                    continue
                
                if next_zone.type_zone == Type_zone.restricted:
                    if drone.start_transit_restricted(
                            next_zone, self.current_turn, connection):
                        turn_movements.append(
                            f"{drone.id_drone}-{connection.name}")
                        moved_this_turn.add(drone.id_drone)
                else:
                    if drone.move_drone(next_zone):
                        turn_movements.append(
                            f"{drone.id_drone}-{next_zone.name}")
                        moved_this_turn.add(drone.id_drone)

            if turn_movements:
                self.history.append(" ".join(turn_movements))

            self.current_turn += 1

    def print_output(self) -> None:
        for line in self.history:
            print(line)
        print(f"Total turns: {self.current_turn}")

    def get_turns(self) -> int:
        return self.current_turn


class Route:
    def __init__(self, path: list[Zone]) -> None:
        self.path = path
        self.assigned_drones: int = 0

    def score(self) -> int:
        return len(self.path) + self.assigned_drones
