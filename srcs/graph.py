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
        for connection in self.connection_dict.values():
#            print(f"{connection} inside con")
 #           print(f"{connection.zone_a} con zone A")
  #          print(f"{connection.zone_b} con zone b")
   #         print(f"{zone_a}zone a")
    #        print(f"{zone_b} zone b")
            if (connection.zone_a.name == zone_a.name and connection.zone_b.name == zone_b.name) or (connection.zone_a.name == zone_b.name and connection.zone_b.name == zone_a.name):
                print(f"{connection.zone_a.name} balsldaksdlas")
                return connection
            if (connection.zone_a is zone_b and connection.zone_b is zone_a) or (connection.zone_a is zone_a and connection.zone_b is zone_b):
                return connection
        return None
