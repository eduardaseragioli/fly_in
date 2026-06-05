from zones import Zone, Type_zone
from connections import Connection
from graph import Graph
from pathlib import Path


class Parser:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def _parse_metadata(self, line: str) -> list:
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

        return [type_zone, color, max_drones]



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
                    self.nb_drones = int(value_drone)
                except ValueError:
                    raise ValueError(f"The {value_drone} is not a int")

            for line in file:
                if line.startswith('#'):
                    pass

                elif line.startswith('start_hub'):
                    parts_start_hub = line.split()
                    name = parts_start_hub[1]
                    x = int(parts_start_hub[2])
                    y = int(parts_start_hub[3])
                    coordinates = x, y

                    type_zone, color, max_drones = self._parse_metadata(line)
                    start_zone = Zone(name, coordinates, type_zone, color, max_drones)
                    zones.append(start_zone)



                elif line.startswith('end_hub'):
                    parts_end_hub = line.split()
                    name = parts_end_hub[1]
                    x = int(parts_end_hub[2])
                    y = int(parts_end_hub[3])
                    coordinates = x, y

                    type_zone, color, max_drones = self._parse_metadata(line)
                    end_zone = Zone(name, coordinates, type_zone, color, max_drones)
                    zones.append(end_zone)


                elif line.startswith('hub'):
                    parts_hub = line.split()
                    name = parts_hub[1]
                    x = int(parts_hub[2])
                    y = int(parts_hub[3])
                    coordinates = x, y

                    type_zone, color, max_drones = self._parse_metadata(line)
                    hub_zone = Zone(name, coordinates, type_zone, color, max_drones)
                    zones.append(hub_zone)


                elif line.startswith('connection'):
                    parts = line.split()
                    zone_names = parts[1].split('-')
                    zona_a = zone_names[0]
                    zona_b = zone_names[1]
                    zone_a = next((z for z in zones if z.name == zona_a), None)
                    zone_b = next((z for z in zones if z.name == zona_b), None)
                    if zone_a is None or zone_b is None:
                        raise ValueError("The zone not in Zones")
                    name = "-".join([zona_a, zona_b])
                    creat_connection = Connection(name, zone_a, zone_b)
                    connection.append(creat_connection)

        if start_zone == None:
            raise ValueError("The start zone can not be null")
        if end_zone == None:
            raise ValueError("The end zone can not be null")

        graph = Graph(start_zone, end_zone)

        for z in zones:
            graph.add_zone(z)
        for c in connection:
            graph.add_connection(c)

        return graph

   

