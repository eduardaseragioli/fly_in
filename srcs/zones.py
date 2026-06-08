from __future__ import annotations
from enum import Enum
from base import Base


class Type_zone(str, Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"

class Zone(Base):

    def __init__(self, name: str, coordinates: tuple[int, int], type_zone: Type_zone = Type_zone.normal, color: str = "None", max_drones: int = 1) -> None:
        self.name = name
        self.coordinates = coordinates
        self.color = color
        self.type_zone = type_zone
        self.max_drones = max_drones
        self.drone_actual: list = []
        self.is_end_zone: bool = False

    def has_capacity(self) -> bool:
        if self.is_end_zone:
            return True
        return len(self.drone_actual) < self.max_drones

    def add_drone(self, drone_actual: Drone) -> bool:
        
        if self.has_capacity() is False:
            return False
        else:
            self.drone_actual.append(drone_actual)
            return True
        
    def remove_drone(self, drone_actual: Drone) -> bool:
        if drone_actual not in self.drone_actual:
            return False
        else:
            self.drone_actual.remove(drone_actual)
            return True
        
    def is_blocked(self) -> bool:
        if self.type_zone == Type_zone.blocked:
            return True 
        else:
            return False

