from __future__ import annotations
from zones import Zone
from enum import Enum
from typing import Optional


class Status(Enum):
    stopped = "stopped"
    in_motion = "in_motion"
    transit_to_restricted = "transit_to_restricted"
    arrived = "arrived"


class Drone:
    def __init__(self, id_drone: str, current_zone: Zone, destination_zone: Zone, current_connection: Optional[Connection] = None) -> None:
        self.id_drone = id_drone
        self.current_zone = current_zone
        self.destination_zone = destination_zone
        self.planned_route: list[Zone] = []
        self.status: Status = Status.stopped
        self.turn_destination: Optional[int] = None
        self.current_connection = current_connection
        self.transit_destination_zone: Optional[Zone] = None

    def move_drone(self, destination_zone: Zone) -> bool:
        capacity = destination_zone.has_capacity()
        if self.destination_zone == destination_zone:
            self.status = Status.arrived
            destination_zone.remove_drone(self)
        if capacity is False:
            return False
        else:
            self.current_zone.remove_drone(self)
            destination_zone.add_drone(self)
            self.current_zone = destination_zone
            self.status = Status.in_motion
            if self.destination_zone == destination_zone:
                self.status = Status.arrived
            if self.planned_route:
                self.planned_route.pop(0)
            return True

    def start_transit_restricted(self, destination_zone: Zone, turno_current: int, connection: Connection) -> bool:
        from connections import Connection
        capacity = connection.has_capacity()
        if capacity is False:
            return False
        else:
            self.current_zone.remove_drone(self)
            connection.add_drone(self)
            self.transit_destination_zone = destination_zone
            self.turn_destination = turno_current + 2
            self.status = Status.transit_to_restricted
            self.current_connection = connection
            return True
