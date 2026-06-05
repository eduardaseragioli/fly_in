from graph import Graph
from drone import Drone
from pathfinder import Pathfinder

class Simulator:
    def __init__(self, graph: Graph, nb_drones: int, pathfinder: Pathfinder) -> None:
        self.graph = graph
        self.pathfinder = pathfinder
        self.current_turn: int = 0
        self.history: list[str] = []
        self.drones: list[Drone] = []
        self.nb_drones = nb_drones

    def create_drone(self) -> None:
        for i in range(1, self.nb_drones + 1):
            drone_id = f"D{i}"
            drone = Drone(drone_id, self.graph.start_zone, self.graph.end_zone)
            self.drones.append(drone)

    def run_simulator(self) -> None:
        while not all(drone.status == Status.arrived for drone in self.drones):
            turn_movements: list[str] = []

            for drone in self.drones:
                if drone.status != Status.arrived:
                    if not drone.planned_route:
                        drone.planned_route = self.pathfinder.find_path(drone.current_zone, drone.destination_zone)
                    if drone.planned_route:
                        next_zone = drone.planned_route[0]
                        if  drone.move_drone(next_zone):
                            turn_movements.append(f"{drone.id_drone}-{next_zone.name}")
                            

            if turn_movements:
                self.history.append(" ".join(turn_movements))                         

            self.current_turn += 1
    
    def print_output(self) -> None:
        for line in self.history:
            print(line)
        print(self.create_drone(self))

    def get_turns(self) -> int:
        return self.current_turn
            
        
        