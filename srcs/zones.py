from __future__ import annotations
from enum import Enum
from base import Base


class Type_zone(str, Enum):
    """Enumeration of possible zone types in the airspace graph."""

    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"

class Zone(Base):
    """Represents a node in the airspace graph with capacity and type constraints."""

    def __init__(self, name: str, coordinates: tuple[int, int], type_zone: Type_zone = Type_zone.normal, color: str = "None", max_drones: int = 1, temp_blocked: bool = False, is_end_zone: bool = False) -> None:
        """Initialize a zone with its properties."""

        self.name: str = name
        self.coordinates: tuple[int, int]  = coordinates
        self.color: str = color
        self.type_zone: Type_zone = type_zone
        self.max_drones: int = max_drones
        self.drone_actual: list[Drone] = []
        self.temp_blocked: bool = temp_blocked
        self.is_end_zone: bool = is_end_zone

    def has_capacity(self) -> bool:
        """Check whether this zone can accept more drones."""

        if self.is_end_zone:
            return True
        return len(self.drone_actual) < self.max_drones

    def add_drone(self, drone_actual: Drone) -> bool:
        """Add a drone to this zone if capacity allows."""
        
        if self.has_capacity() is False:
            return False
        else:
            self.drone_actual.append(drone_actual)
            return True
        
    def remove_drone(self, drone_actual: Drone) -> bool:
        """Remove a drone from this zone."""

        if drone_actual not in self.drone_actual:
            return False
        else:
            self.drone_actual.remove(drone_actual)
            return True
        
    def is_blocked(self) -> bool:
        """Check whether this zone is permanently blocked."""
        
        if self.type_zone == Type_zone.blocked:
            return True 
        else:
            return False
