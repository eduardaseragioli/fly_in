from __future__ import annotations
from graph import Graph
from zones import Zone, Type_zone
from typing import Optional
import heapq


class ReservationTable:
    def __init__(self):
        self.zone_reservations: dict[tuple, int] = {}
        self.edge_reservations: dict[tuple, int] = {}

    def is_zone_available(self, zone_name: str, turn: int, max_capacity: int) -> bool:
        return self.zone_reservations.get((zone_name, turn), 0) < max_capacity

    def is_edge_available(self, name_a: str, name_b: str, turn: int, max_capacity: int) -> bool:
        key = tuple(sorted([name_a, name_b]))
        return self.edge_reservations.get((key, turn), 0) < max_capacity

    def reserve_zone(self, zone_name: str, turn: int):
        self.zone_reservations[(zone_name, turn)] = \
            self.zone_reservations.get((zone_name, turn), 0) + 1

    def reserve_edge(self, name_a: str, name_b: str, turn: int):
        key = tuple(sorted([name_a, name_b]))
        self.edge_reservations[(key, turn)] = \
            self.edge_reservations.get((key, turn), 0) + 1


class Pathfinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_path(self, start_hub: Optional[Zone], end_hub: Optional[Zone]) -> list[Zone]:
        """Dijkstra simples sem reservas, retorna lista de zonas."""
        dist: dict[Zone, int] = {start_hub: 0}
        prev: dict[Zone, Zone] = {}
        visited: set[Zone] = set()
        heap = [(0, 0, start_hub)]
        counter = 0

        while heap:
            d, _, zone = heapq.heappop(heap)
            if zone in visited:
                continue
            visited.add(zone)

            if zone == end_hub:
                path = [end_hub]
                cur = end_hub
                while cur in prev:
                    cur = prev[cur]
                    path.append(cur)
                path.reverse()
                return path

            for neighbor in self.graph.get_neighbors(zone):
                if neighbor.type_zone == Type_zone.blocked:
                    continue
                cost = 2 if neighbor.type_zone == Type_zone.restricted else 1
                nd = d + cost
                if neighbor not in dist or nd < dist[neighbor]:
                    dist[neighbor] = nd
                    prev[neighbor] = zone
                    counter += 1
                    heapq.heappush(heap, (nd, counter, neighbor))
        return []

    def find_path_with_reservations(
        self,
        start_hub: Optional[Zone],
        end_hub: Optional[Zone],
        table: ReservationTable,
        start_turn: int = 0,
        max_turn: int = 200
    ) -> list[tuple[Zone, int]]:
        """
        Dijkstra espaço-tempo com reservation table.
        Retorna lista de (zona, turno) com os turnos absolutos de chegada.
        """
        start_node = (start_hub, start_turn)
        dist: dict[tuple, float] = {start_node: 0}
        prev: dict[tuple, Optional[tuple]] = {start_node: None}
        visited: set[tuple] = set()
        heap = [(0, 0, start_hub, start_turn)]
        counter = 0

        while heap:
            d, _, zone, turn = heapq.heappop(heap)
            node = (zone, turn)

            if node in visited:
                continue
            visited.add(node)

            if zone == end_hub:
                # Reconstruir caminho
                path = []
                cur = node
                while cur is not None:
                    path.append(cur)
                    cur = prev[cur]
                path.reverse()
                return path

            if turn >= max_turn:
                continue

            # Mover para vizinhos
            for neighbor in self.graph.get_neighbors(zone):
                if neighbor.type_zone == Type_zone.blocked:
                    continue

                weight = 2 if neighbor.type_zone == Type_zone.restricted else 1
                next_turn = turn + weight

                if next_turn > max_turn:
                    continue

                # Verificar capacidade da conexão
                conn = self.graph.get_connection(zone, neighbor)
                if conn and not table.is_edge_available(
                        zone.name, neighbor.name, turn, conn.max_link_capacity):
                    continue

                # Verificar capacidade da zona destino (exceto end_hub e start_hub)
                if neighbor != end_hub and neighbor != start_hub:
                    # Para restricted, verificar todos os turnos de ocupação
                    if neighbor.type_zone == Type_zone.restricted:
                        ok = all(
                            table.is_zone_available(neighbor.name, t, neighbor.max_drones)
                            for t in range(turn + 1, next_turn + 1)
                        )
                    else:
                        ok = table.is_zone_available(
                            neighbor.name, next_turn, neighbor.max_drones)
                    if not ok:
                        continue

                next_node = (neighbor, next_turn)
                new_dist = d + weight
                if new_dist < dist.get(next_node, float('inf')):
                    dist[next_node] = new_dist
                    prev[next_node] = node
                    counter += 1
                    heapq.heappush(heap, (new_dist, counter, neighbor, next_turn))

            # Esperar na zona atual
            wait_turn = turn + 1
            if wait_turn <= max_turn:
                can_wait = (
                    zone == start_hub or
                    table.is_zone_available(zone.name, wait_turn, zone.max_drones)
                )
                if can_wait:
                    wait_node = (zone, wait_turn)
                    wait_dist = d + 1
                    if wait_dist < dist.get(wait_node, float('inf')):
                        dist[wait_node] = wait_dist
                        prev[wait_node] = node
                        counter += 1
                        heapq.heappush(heap, (wait_dist, counter, zone, wait_turn))

        return []