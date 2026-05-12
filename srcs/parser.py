from zones import Zone, Type_zone
from connections import Connection
from graph import Graph
from pathlib import Path
from typing import Optional

class Parser:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def parse(self) -> Graph:
        start_zone: Optional[Zone] = None
        end_zone: Optional[Zone] = None
        zones: list[Zone] = []
        connection: list[Connection] = []
        with open(self.file_path, 'r') as file:
            line = file.readline()
            if line.startswith('nb_drones: '): 
                nb_drones_split= line.split(":")
                value_drone = nb_drones_split[1].strip()
                try:
                    value_drone = int(value_drone)
                except ValueError:
                    raise ValueError("The {value_drone} is not a int")
            for line in file:
                if line.startswith('#'):
                    pass
                elif line.startswith('start_hub'):
                    parts_start_hub = line.split()
                    name = parts_start_hub[1]
                    x = int(parts_start_hub[2])
                    y = int(parts_start_hub[3])
                    start_zone = Zone(name, (x, y))
                elif line.startswith('end_hub'):
                    parts_end_hub = line.split()
                    name = parts_end_hub[1]
                    x = int(parts_end_hub[2])
                    y = int(parts_end_hub[3])
                    end_zone = Zone(name, (x, y))
                elif line.startswith('hub'):
                    parts_hub = line.split()
                    name = parts_hub[1]
                    x = int(parts_hub[2])
                    y = int(parts_hub[3])
                    
                    if '[' in line:
                        type_zone = Type_zone.normal
                        color = "None"
                        max_drones = 1
                        metadata = line[line.index('[') + 1 : line.index(']')]
                        for pair in metadata.split():
                            key, value = pair.split('=')
                            if key == "zone":
                                type_zone = Type_zone(value)
                            elif key == "color":
                                color = value
                            elif key == "max_drones":
                                max_drones = int(value)
                    else:
                        type_zone = Type_zone.normal
                        color = "None"
                        max_drones = 1

                    coordinates = [x, y] 
                    create_zone = Zone(name, coordinates, type_zone, color, max_drones)
                    zones.append(create_zone)
                elif line.startswith('connection'):
                    connection = 

        return Graph(start_zone, end_zone)

   

