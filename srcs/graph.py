from __future__ import annotations
from zones import Zone
from connections import Connection
from typing import Optional


class Graph:
    def __init__(self, start_zone: Zone, end_zone: Zone) -> None:
        self.zone_dict: dict[str, Zone] = {}
        self.connection_dict: dict[str, Connection] = {}
        self.start_zone = start_zone
        self.end_zone = end_zone

    def add_zone(self, zone_will_installed: Zone) -> bool:
        if zone_will_installed.name in self.zone_dict:
            return False
        else:
            self.zone_dict[zone_will_installed.name] = zone_will_installed
            return True

    def add_connection(self, connection_will_installed: Connection) -> bool:
        if connection_will_installed.name in self.connection_dict:
            return False
        else:
            self.connection_dict[connection_will_installed.name] = connection_will_installed
            return True

    def get_neighbors(self, zone_neighbors: Zone) -> list[Zone]:
        zone_list: list[Zone] = []

        for connection in self.connection_dict.values():
            if zone_neighbors == connection.zone_a:
                if connection.zone_b.is_blocked() or connection.zone_b.temp_blocked:
                    pass
                elif connection.temp_blocked is True:
                    pass
                else:
                    zone_list.append(connection.zone_b)

            elif zone_neighbors == connection.zone_b:
                if connection.zone_a.is_blocked() or connection.zone_a.temp_blocked:
                    pass
                elif connection.temp_blocked is True:
                    pass
                else:
                    zone_list.append(connection.zone_a)
        return zone_list

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Optional[Connection]:
        if zone_a is None or zone_b is None:
            return None
        
        for connection in self.connection_dict.values():
            zone_a_name = zone_a.name if zone_a else None
            zone_b_name = zone_b.name if zone_b else None
            
            if zone_a_name is None or zone_b_name is None:
                continue
            
            if ((connection.zone_a.name == zone_a_name and
                 connection.zone_b.name == zone_b_name) or
                (connection.zone_a.name == zone_b_name and
                 connection.zone_b.name == zone_a_name)):
                return connection
        return None
