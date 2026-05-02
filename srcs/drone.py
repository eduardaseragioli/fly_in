from zones import Zone
from enum import Enum

class Status(Enum):
    stopped = "stopped"
    in_motion = "in_motion"
    transit_to_restricted = "transit_to_restricted"
    arrived = "arrived"


class Drone:
    def __init__(self, id_drone: str, current_zone: Zone, destination_zone: Zone, planned_route: list, status: Status, turn_destination: int) -> None:
        self.id_drone = id_drone
        self.current_zone = current_zone
        self.destination_zone = destination_zone
        self.planned_route = planned_route
        self.status = status
        self.turn_destination = turn_destination