from __future__ import annotations
from graph import Graph
from pathfinder import Pathfinder, ReservationTable
from drone import Drone, Status
from zones import Zone


class Simulator:
    """Plans and executes the drone routing simulation turn by turn."""

    def __init__(self,
                 graph: Graph,
                 nb_drones: int,
                 pathfinder: Pathfinder) -> None:
        """Initialize the simulator with a graph,
                drone count, and pathfinder."""

        self.graph: Graph = graph
        self.pathfinder: Pathfinder = pathfinder
        self.current_turn: int = 0
        self.history: list[str] = []
        self.drones: list[Drone] = []
        self.nb_drones: int = nb_drones

    def _place_drone_at_start(self, drone: Drone) -> bool:
        """Place a drone at the start zone using Zone.add_drone."""

        return self.graph.start_zone.add_drone(drone)

    def _move_drone_to_zone(self, drone: Drone, destination: Zone) -> bool:
        """Move a drone between zones using the Zone and Drone APIs"""

        if not destination.has_capacity():
            return False

        conn = self.graph.get_connection(drone.current_zone, destination)
        if conn:
            if not conn.has_capacity():
                return False
            conn.add_drone(drone)

        drone.move_drone(destination)

        if conn:
            conn.remove_drone(drone)

        return True

    def create_drone(self) -> None:
        """Plan collision-free paths for all
                drones using the reservation table."""

        table: ReservationTable = ReservationTable()

        for i in range(1, self.nb_drones + 1):
            drone_id: str = f"D{i}"
            drone: Drone = Drone(
                drone_id, self.graph.start_zone, self.graph.end_zone)

            path: list[tuple[Zone, int]] = (
                self.pathfinder.find_path_with_reservations(
                    self.graph.start_zone, self.graph.end_zone,
                    table, start_turn=0)
            )

            if not path:
                self.drones.append(drone)
                continue

            table.reserve_path(
                path, self.graph, self.graph.start_zone, self.graph.end_zone)
            print(f"{drone_id}: {[(z.name, t) for z, t in path]}")

            drone.planned_path = [(z, t)
                                  for z, t in path
                                  if z != self.graph.start_zone]

            drone.path_index = 0
            drone.start_turn = 0
            self._place_drone_at_start(drone)
            self.drones.append(drone)

    def run_simulator(self) -> None:
        """Execute the simulation by moving all
                drones along their planned paths."""

        delivered: set[str] = set()
        self.current_turn = 0
        max_turns = -1

        for drone in self.drones:
            for path in drone.planned_path:
                if path[1] > max_turns:
                    max_turns = path[1]
        for drone in self.drones:
            for n in range(0, drone.planned_path[0][1]):
                drone.planned_path.insert(n, (self.graph.start_zone, n))
            last_turn = None
            i = 0
            for n, turn in enumerate(drone.planned_path):
                zone = turn[0]
                turn_nbr = turn[1]
                if turn_nbr != i:
                    drone.planned_path.insert(n, (last_turn[0], i))
                i += 1
                last_turn = turn

        while len(delivered) < len(self.drones) \
                and self.current_turn < max_turns:
            self.current_turn += 1
            movements: list[str] = []

            for drone in self.drones:
                if drone.status == Status.arrived:
                    continue

                path = drone.planned_path
                if not path:
                    drone.status = Status.arrived
                    delivered.add(drone.id_drone)
                    continue

                while (drone.path_index < len(path) and
                       path[drone.path_index][1] < self.current_turn):
                    drone.path_index += 1
                if drone.path_index >= len(path):
                    drone.status = Status.arrived
                    delivered.add(drone.id_drone)
                    continue

                zone, target_turn = path[drone.path_index]
                if target_turn == self.current_turn and zone != drone.current_zone:
                    moved = self._move_drone_to_zone(drone, zone)

                    if moved:
                        movements.append(f"{drone.id_drone}-{zone.name}")
                        drone.path_index += 1

                        if zone == self.graph.end_zone:
                            delivered.add(drone.id_drone)

            #if movements:
            self.history.append(" ".join(movements))

    def print_output(self) -> None:
        """Print the simulation history and total turn count to stdout."""

        for line in self.history:
            print(line)
        print(f"Total turns: {self.current_turn}")

    def get_turns(self) -> int:
        """Return the total number of turns taken by the simulation."""
        return self.current_turn
