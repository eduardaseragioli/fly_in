from __future__ import annotations
from typing import Optional
from zones import Zone, Type_zone
from connections import Connection
from graph import Graph
from pathlib import Path


class Parser:
    """Parses a map configuration file and builds a Graph object."""

    def __init__(self, file_path: Path) -> None:
        """Initialize the parser with a path to the map file."""

        self.file_path: Path = file_path
        self.nb_drones: int = 0

    def _parse_metadata(self, line: str) -> tuple[Type_zone, str, int]:
        """Extract zone type, color, and max_drones from a metadata block"""

        if '[' in line:
            type_zone: Type_zone = Type_zone.normal
            color: str = "None"
            max_drones: int = 1
            metadata = line[line.index('[') + 1: line.index(']')]

            for pair in metadata.split():
                key, value = pair.split('=')
                if key == "zone":
                    type_zone = Type_zone(value)
                elif key == "color":
                    color = value
                elif key == "max_drones":
                    max_drones = int(value)
                    if max_drones <= 0:
                        raise ValueError("max_drones must be greater than 0")
        else:
            type_zone = Type_zone.normal
            color = "None"
            max_drones = 1

        return type_zone, color, max_drones

    def _parse_connection_metadata(self, line: str) -> int:
        """Extract max_link_capacity from a connection metadata block."""

        max_link_capacity = 1
        if '[' in line:
            begin = line.index('[') + 1
            finished = line.index(']')
            metadata = line[begin: finished]

            for pair in metadata.split():
                key, value = pair.split('=')

                if key == "max_link_capacity":
                    max_link_capacity = int(value)

                    if max_link_capacity <= 0:
                        raise ValueError(
                            "max_link_capacity must be greater than 0")
        return max_link_capacity

    def parse(self) -> Graph:
        """Parse the map file and construct a Graph
            with zones and connections."""

        start_zone: Optional[Zone] = None
        end_zone: Optional[Zone] = None
        zones: list[Zone] = []
        connection: list[Connection] = []
        zone_names: set[str] = set()
        connection_names: set[tuple[str, str]] = set()

        with open(self.file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if line.startswith('#') or not line:
                    continue

                if line.startswith('nb_drones: '):
                    nb_drones_split = line.split(":")
                    value_drone = nb_drones_split[1].strip()
                    try:
                        self.nb_drones = int(value_drone)
                    except ValueError:
                        raise ValueError(
                            f"Line {line_number}:"
                            + "The {value_drone} is not a int")

                    if self.nb_drones <= 0:
                        raise ValueError(
                            f"Line {line_number}: nb_drones"
                            "must be greater than 0")

                elif line.startswith('start_hub'):
                    parts_start_hub = line.split()
                    name = parts_start_hub[1]

                    if "-" in name:
                        raise ValueError(
                            f"Line {line_number}: Zone"
                            "names can't contain '-'")

                    if name in zone_names:
                        raise ValueError(
                            f"Line {line_number}: Duplicate zone name: {name}")
                    zone_names.add(name)

                    x = int(parts_start_hub[2])
                    y = int(parts_start_hub[3])
                    coordinates = x, y

                    type_zone, color, max_drones = self._parse_metadata(line)
                    start_zone = Zone(name, coordinates,
                                      type_zone, color, max_drones)
                    zones.append(start_zone)

                elif line.startswith('end_hub'):
                    parts_end_hub = line.split()
                    name = parts_end_hub[1]

                    if "-" in name:
                        raise ValueError(
                            f"Line {line_number}:"
                            "Zone names can't contain '-'")

                    if name in zone_names:
                        raise ValueError(
                            f"Line {line_number}: Duplicate zone name: {name}")
                    zone_names.add(name)

                    x = int(parts_end_hub[2])
                    y = int(parts_end_hub[3])
                    coordinates = x, y

                    type_zone, color, max_drones = self._parse_metadata(line)
                    end_zone = Zone(name, coordinates,
                                    type_zone, color, max_drones)
                    zones.append(end_zone)

                elif line.startswith('hub'):
                    parts_hub = line.split()
                    name = parts_hub[1]

                    if "-" in name:
                        raise ValueError(
                            f"Line {line_number}: Zone"
                            "names can't contain '-'")

                    if name in zone_names:
                        raise ValueError(
                            f"Line {line_number}: Duplicate zone name: {name}")
                    zone_names.add(name)

                    x = int(parts_hub[2])
                    y = int(parts_hub[3])
                    coordinates = x, y

                    type_zone, color, max_drones = self._parse_metadata(line)
                    hub_zone = Zone(name, coordinates,
                                    type_zone, color, max_drones)
                    zones.append(hub_zone)

                elif line.startswith('connection'):
                    parts = line.split()
                    conn_names = parts[1].split('-')
                    zona_a = conn_names[0]
                    zona_b = conn_names[1]

                    zone_a = next((z for z in zones if z.name == zona_a), None)
                    zone_b = next((z for z in zones if z.name == zona_b), None)

                    if zone_a is None or zone_b is None:
                        raise ValueError(
                            f"Line {line_number}: Connection"
                            "references unknown zone")

                    connection_key = tuple(sorted((zona_a, zona_b)))
                    if connection_key in connection_names:
                        raise ValueError(
                            f"Line {line_number}: Duplicate"
                            + "connections: {zona_a}-{zona_b}")
                    connection_names.add(connection_key)

                    name = "-".join([zona_a, zona_b])

                    max_link_capacity = self._parse_connection_metadata(line)

                    creat_connection = Connection(
                        name, zone_a, zone_b, max_link_capacity)
                    connection.append(creat_connection)

        if self.nb_drones == 0:
            raise ValueError("Missing nb_drones definition")
        if start_zone is None:
            raise ValueError("Missing start_hub definition")
        if end_zone is None:
            raise ValueError("Missing end_hub definition")

        graph = Graph(start_zone, end_zone)

        for z in zones:
            graph.add_zone(z)
        for c in connection:
            graph.add_connection(c)

        return graph
