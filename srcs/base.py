from abc import ABC, abstractmethod

class Base(ABC):
        
        @abstractmethod
        def has_capacity(self) -> bool:
                pass
        
        @abstractmethod
        def add_drone(self, drone_actual: Drone) -> bool:
                pass
        
        @abstractmethod
        def remove_drone(self, drone_actual: Drone) -> bool:
                pass
        
