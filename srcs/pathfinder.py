from __future__ import annotations
from parser import Parser
from graph import Graph
from zones import Zone
from typing import Optional
from zones import Type_zone, Zone
from connections import Connection
import heapq


class Pathfinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_path(self, start_hub: Optional[Zone], end_hub: Optional[Zone]) -> list[Zone]:
        accumulated_distances: dict[Zone, int] = {
            start_hub: 0
        }
        visited_path: dict[Zone, Zone] = {}
        unvisited_zone = [(0, 0, start_hub)]
        neighbor: Zone
        counter = 0

        while unvisited_zone:

            current_distance, _, current_zone = heapq.heappop(unvisited_zone)

            if current_zone == end_hub:
                destination = end_hub
                reverse_path: list = []
                current = destination
                while current in visited_path:
                    reverse_path.append(current)
                    current = visited_path[current]
                path_found = reverse_path[::-1]
                return path_found

            for neighbor in self.graph.get_neighbors(current_zone):

                if neighbor.type_zone == Type_zone.normal:
                    cost = 1
                elif neighbor.type_zone == Type_zone.restricted:
                    cost = 2
                elif neighbor.type_zone == Type_zone.priority:
                    cost = 1
                else:
                    cost = 1

                new_distance = current_distance + cost

                if neighbor not in accumulated_distances or new_distance < accumulated_distances[neighbor]:
                    accumulated_distances[neighbor] = new_distance
                    visited_path[neighbor] = current_zone

                    heapq.heappush(
                        unvisited_zone, (new_distance, counter, neighbor))
                    counter += 1

    def find_k_paths(self, start_hub: Optional[Zone], end_hub: Optional[Zone], k: int) -> list[list[Zone]]:
        first_path = self.find_path(start_hub, end_hub)
        if not first_path:
            return []

        k_paths = [first_path]
        candidates: list = []

        for i in range(k - 1):
            current_path = k_paths[i]
            for j in range(len(current_path)):
                super_node = current_path[j]
                base_path = current_path[:j + 1]

                removed_connections: list = []
                removed_zones: list = []

                for connection in list(self.graph.connection_dict.values()):
                    if j > 0:
                        prev_node = current_path[j - 1]
                        if (connection.zone_a == super_node and connection.zone_b == prev_node) or (connection.zone_a == prev_node and connection.zone_b == super_node):
                            connection.is_blocked = True
                            removed_connections.append(connection)
