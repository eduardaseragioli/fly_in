from __future__ import annotations
from zones import Zone
from base import Base

class Connection(Base):

    def __init__(self, name: str, zone_a: Zone, zone_b: Zone, max_link_capacity: int = 1, is_blocked: bool = False) -> None:
        self.name = name
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity
        self.drone_transit: list = []
        self.is_blocked: bool = False

    def has_capacity(self) -> bool:
        if len(self.drone_transit) >= self.max_link_capacity:
            return False
        else:
            return True
        
    def add_drone(self, drone_actual: Drone) -> bool:
        if self.has_capacity() is False:
            return False
        else:
            self.drone_transit.append(drone_actual)
            return True
        
    def remove_drone(self, drone_actual: Drone) -> bool:
        if drone_actual not in self.drone_transit:
            return False
        else:
            self.drone_transit.remove(drone_actual)
            return True

