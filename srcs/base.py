from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from drone import Drone


class Base(ABC):
    """Abstract base class for objects that can hold
        drones with capacity limits."""

    @abstractmethod
    def has_capacity(self) -> bool:
        """Check if this object accepts more drones."""
        pass

    @abstractmethod
    def add_drone(self, drone_actual: Drone) -> bool:
        """Add a drone to this object if capacity allows."""
        pass

    @abstractmethod
    def remove_drone(self, drone_actual: Drone) -> bool:
        """Remove a drone from this object."""
        pass
