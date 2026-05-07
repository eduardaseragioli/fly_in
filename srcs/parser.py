from zones import Zone
from connections import Connection
from graph import Graph
from pathlib import Path

class Parser:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def parse(self) -> Graph:
        with open(self.file_path, 'r') as file:
            line = file.readline()
            if line.startswith('nb_drones: '): 
                nb_drones_split= line.split(":").strip()
                value_drone = nb_drones_split[1]
                try:
                    value_drone = int(value_drone)
                except ValueError:
                    raise ValueError("The {value_drone} is not a int")
                
            for line in file:
                if line.startswith('#'):
                    pass
                elif line.startswith('start_hub'):
                    start_hub = 
                elif line.startswith('end_hub'):
                    end_hub = 
                elif line.startswith('hub'):
                    hub = 
                elif line.startswith('connection'):
                    connection = 

        return Graph(start_zone, end_zone)

   

