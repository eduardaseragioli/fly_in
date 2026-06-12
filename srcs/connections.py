from __future__ import annotations
from zones import Zone
from base import Base


class Connection(Base):
    """Represents a directional link between two zones with capacity constraints."""

    def __init__(self, name: str, zone_a: Zone, zone_b: Zone, max_link_capacity: int = 1) -> None:
        """Initialize a connection between two zones"""
        self.name: str = name
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max_link_capacity: int = max_link_capacity
        self.drone_transit: list[Drone] = []
        self.temp_blocked: bool = False

    def has_capacity(self) -> bool:
        """Check whether this connection can accept more drones in transit."""
        if len(self.drone_transit) >= self.max_link_capacity:
            return False
        else:
            return True

    def add_drone(self, drone_actual: Drone) -> bool:
        """Add a drone to this connection's transit list if capacity allows."""
        if self.has_capacity() is False:
            return False
        else:
            self.drone_transit.append(drone_actual)
            return True

    def remove_drone(self, drone_actual: Drone) -> bool:
        """Remove a drone from this connection's transit list."""
        if drone_actual not in self.drone_transit:
            return False
        else:
            self.drone_transit.remove(drone_actual)
            return True
            