from __future__ import annotations
from graph import Graph
from zones import Zone, Type_zone
from typing import Optional
import heapq


class ReservationTable:
    """Tracks zone and edge occupancy by turn for cooperative pathfinding."""

    def __init__(self) -> None:
        """Initialize empty reservation tables for zones and edges."""

        self.zone_reservations: dict[tuple[str, int], int] = {}
        self.connection_reservations: dict[
            tuple[tuple[str, str], int], int
        ] = {}

    def is_zone_available(self,
                          zone_name: str,
                          turn: int,
                          max_capacity: int) -> bool:
        """Check whether a zone has free capacity at a given turn."""
        return self.zone_reservations.get((zone_name, turn), 0) < max_capacity

    def is_connection_available(self,
                                name_a: str,
                                name_b: str,
                                turn: int,
                                max_capacity: int) -> bool:
        """Check whether a connection has free capacity at a given turn."""

        if name_a <= name_b:
            key: tuple[str, str] = (name_a, name_b)
        else:
            key = (name_b, name_a)
        return self.connection_reservations.get((key, turn), 0) < max_capacity

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        """Reserve one slot in a zone for a specific turn."""
        self.zone_reservations[(zone_name, turn)] = \
            self.zone_reservations.get((zone_name, turn), 0) + 1

    def reserve_edge(self, name_a: str, name_b: str, turn: int) -> None:
        """Reserve one slot on an edge for a specific turn."""

        edge_key: tuple[str, str] = (name_a, name_b) if name_a <= name_b \
            else (name_b, name_a)
        key = (edge_key, turn)
        self.connection_reservations[key] = self.connection_reservations.get(
            key, 0) + 1

    def reserve_path(self, path: list[tuple[Zone, int]],
                     graph: Graph,
                     start_zone: Zone,
                     end_zone: Zone) -> None:
        """Reserve all zones and edges along a planned path.

        Every turn of the path is now an explicit (zone, turn) entry
        (including the mandatory settle turn spent inside a restricted
        zone), so there are never any gaps left to backfill here.
        """

        for idx, (zone, turn) in enumerate(path):
            if zone != end_zone and zone != start_zone:
                self.reserve_zone(zone.name, turn)
            if idx < len(path) - 1:
                next_zone, _ = path[idx + 1]
                if next_zone != zone:
                    conn = graph.get_connection(zone, next_zone)
                    if conn:
                        self.reserve_edge(zone.name, next_zone.name, turn)


class Pathfinder:
    """Finds optimal collision-free paths through the graph using Dijkstra.

    Space-time search state: (zone, turn, settled).
    'settled' is False the instant a drone arrives at a restricted zone,
    and becomes True only after it has spent one additional full turn
    there. A drone may only leave a restricted zone once settled.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the pathfinder with a graph."""
        self.graph: Graph = graph

    def find_path_with_reservations(
        self,
        start_hub: Zone,
        end_hub: Zone,
        table: ReservationTable,
        start_turn: int = 0,
        max_turn: int = 200
    ) -> list[tuple[Zone, int]]:
        """Find a collision-free path using space-time
                Dijkstra with a reservation table."""

        StateKey = tuple[Zone, int, bool]

        start_node: StateKey = (start_hub, start_turn, True)
        dist: dict[StateKey, float] = {start_node: 0}
        prev: dict[StateKey, Optional[StateKey]] = {start_node: None}
        heap: list[tuple[float, int, int, Zone, int, bool]] = [
            (0, 0, 0, start_hub, start_turn, True)]
        counter: int = 0

        while heap:
            d, _, _, zone, turn, settled = heapq.heappop(heap)
            node: StateKey = (zone, turn, settled)

            if zone == end_hub:
                path: list[tuple[Zone, int]] = []
                cur: Optional[StateKey] = node
                while cur is not None:
                    path.append((cur[0], cur[1]))
                    cur = prev[cur]
                path.reverse()
                return path

            if turn >= max_turn:
                continue

            may_leave = zone.type_zone != Type_zone.restricted or settled

            if may_leave:
                for neighbor in self.graph.get_neighbors(zone):
                    if neighbor.type_zone == Type_zone.blocked:
                        continue

                    next_turn = turn + 1
                    if next_turn > max_turn:
                        continue

                    conn = self.graph.get_connection(zone, neighbor)
                    if conn and not table.is_connection_available(
                            zone.name, neighbor.name, turn,
                            conn.max_link_capacity):
                        continue

                    if neighbor != end_hub:
                        if not table.is_zone_available(
                                neighbor.name, next_turn,
                                neighbor.max_drones):
                            continue

                    neighbor_settled = \
                        neighbor.type_zone != Type_zone.restricted
                    next_node: StateKey = (
                        neighbor, next_turn, neighbor_settled)
                    new_dist = d + 1
                    if new_dist < dist.get(next_node, float('inf')):
                        dist[next_node] = new_dist
                        prev[next_node] = node
                        counter += 1

                        priority_bonus = -1 \
                            if neighbor.type_zone == Type_zone.priority \
                            else 0

                        heapq.heappush(
                            heap, (new_dist, priority_bonus, counter,
                                   neighbor, next_turn, neighbor_settled))

            wait_turn = turn + 1
            if wait_turn <= max_turn:
                wait_settled = True
                can_wait = (
                    zone == start_hub or
                    table.is_zone_available(
                        zone.name, wait_turn, zone.max_drones)
                )
                if can_wait:
                    wait_node: StateKey = (zone, wait_turn, wait_settled)
                    wait_dist = d + 1
                    if wait_dist < dist.get(wait_node, float('inf')):
                        dist[wait_node] = wait_dist
                        prev[wait_node] = node
                        counter += 1
                        heapq.heappush(
                            heap, (wait_dist, 0, counter,
                                   zone, wait_turn, wait_settled))

        return []
