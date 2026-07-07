from __future__ import annotations
from zones import Zone
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from connections import Connection


class Status(Enum):
    """Represents the current movement state of a drone."""
    stopped = "stopped"
    in_motion = "in_motion"
    transit_to_restricted = "transit_to_restricted"
    arrived = "arrived"


class Drone:
    """Represents a drone navigating through the
        graph from start to destination."""

    def __init__(self, id_drone: str, current_zone: Zone,
                 destination_zone: Zone,
                 current_connection: Optional[Connection] = None) -> None:
        """Initialize a drone with its starting position and destination."""
        self.id_drone: str = id_drone
        self.current_zone: Zone = current_zone
        self.destination_zone: Zone = destination_zone
        self.planned_route: list[Zone] = []
        self.planned_path: list[tuple[Zone, int]] = []
        self.path_index: int = 0
        self.status: Status = Status.stopped
        self.turn_destination: Optional[int] = None
        self.current_connection: Optional[Connection] = current_connection
        self.transit_destination_zone: Optional[Zone] = None
        self.start_turn: int = 0

    def move_drone(self, destination_zone: Zone) -> bool:
        """Move the drone to an adjacent zone if it has capacity."""

        if not destination_zone.has_capacity():
            return False

        self.current_zone.remove_drone(self)
        self.current_zone = destination_zone

        if self.planned_route:
            self.planned_route.pop(0)

        if self.destination_zone == destination_zone:
            self.status = Status.arrived

        else:
            destination_zone.add_drone(self)
            self.status = Status.in_motion

        self.time_in_zone = 0
        return True

    def start_transit_restricted(self, destination_zone: Zone,
                                 turno_current: int,
                                 connection: Connection) -> bool:
        """Begin a two-turn transit through a restricted
                zone via a connection."""

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
