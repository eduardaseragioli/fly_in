############ simulator.py (ficheiro completo) ############
from __future__ import annotations
from graph import Graph
from pathfinder import Pathfinder, ReservationTable
from drone import Drone, Status
from zones import Zone, Type_zone


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
                print(
                    f"Warning: no valid path found for {drone_id} "
                    f"(end zone unreachable, or blocked by capacity "
                    f"within the turn limit)."
                )
                self.drones.append(drone)
                continue

            table.reserve_path(
                path, self.graph, self.graph.start_zone, self.graph.end_zone)

            drone.planned_path = [(z, t)
                                  for z, t in path
                                  if z != self.graph.start_zone]

            drone.path_index = 0
            drone.start_turn = 0
            self._place_drone_at_start(drone)
            self.drones.append(drone)

    def _advance_drone(self, drone: Drone, movements: list[str]) -> None:
        """Advance a single drone by one simulation step.

        A path entry whose zone matches the drone's current zone is a
        genuine mandatory-settle turn inside a restricted zone (the raw
        path now always contains an explicit entry per turn, no gaps).
        It is displayed, but no real move is attempted since the drone
        is already there. Any other entry triggers a real, capacity
        checked move; if that move fails, it is retried the next turn
        instead of being skipped.
        """

        path = drone.planned_path

        while (drone.path_index < len(path) and
               path[drone.path_index][1] <= self.current_turn and
               path[drone.path_index][0] == drone.current_zone):
            zone, _ = path[drone.path_index]
            if zone.type_zone == Type_zone.restricted:
                movements.append(f"{drone.id_drone}-{zone.name}")
            drone.path_index += 1

        if drone.path_index >= len(path):
            drone.status = Status.arrived
            return

        zone, target_turn = path[drone.path_index]
        if target_turn <= self.current_turn and zone != drone.current_zone:
            moved = self._move_drone_to_zone(drone, zone)
            if moved:
                movements.append(f"{drone.id_drone}-{zone.name}")
                drone.path_index += 1
                if zone == self.graph.end_zone:
                    drone.status = Status.arrived

    def run_simulator(self) -> None:
        """Execute the simulation by moving all
                drones along their planned paths."""

        delivered: set[str] = set()
        self.current_turn = 0
        planned_max_turns = -1

        for drone in self.drones:
            for entry in drone.planned_path:
                if entry[1] > planned_max_turns:
                    planned_max_turns = entry[1]

        safety_margin = len(self.drones) + 1
        max_turns = planned_max_turns + safety_margin
        while len(delivered) < len(self.drones) \
                and self.current_turn < max_turns:
            self.current_turn += 1
            movements: list[str] = []

            for drone in self.drones:
                if drone.status == Status.arrived:
                    if drone.id_drone not in delivered:
                        delivered.add(drone.id_drone)
                    continue
                if not drone.planned_path:
                    drone.status = Status.arrived
                    delivered.add(drone.id_drone)
                    continue

                self._advance_drone(drone, movements)

                if drone.status == Status.arrived:
                    delivered.add(drone.id_drone)

            self.history.append(" ".join(movements))

    def print_output(self) -> None:
        """Print the simulation history and total turn count to stdout."""

        for line in self.history:
            print(line)
        print(f"Total turns: {self.current_turn}")

    def get_turns(self) -> int:
        """Return the total number of turns taken by the simulation."""
        return self.current_turn
