from graph import Graph
from zones import Zone, Type_zone
import pygame
from pygame.surface import Surface
import os


class Visualizer:
    """Renders the airspace graph and animates drone movements using pygame."""

    def __init__(self, graph: Graph, history: list[str], total_turns: int) -> None:
        """Initialize the visualizer with the graph and simulation history."""

        self.graph: Graph = graph
        self.history: list[str] = history
        self.total_turns = total_turns

        self.height: int = 1000
        self.width: int = 1000
        self.screen: Surface | None = None
        self.fly_in_status: bool = False
        self.current_turn: int = 0
        self.CORES: dict[str, tuple[int, int, int]] = {
            "normal": (0, 176, 112),
            "blocked": (193, 43, 59),
            "restricted": (47, 72, 88),
            "priority": (255, 215, 0),
            "start": (225, 182, 193),
            "end": (216, 191, 216),

            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "green": (0, 255, 0),
            "pink": (255, 192, 203)
        }

        self.color_map: dict[str, tuple[int, int, int]] = {
            "green":   (34, 177,  76),
            "blue":    (52,  131, 235),
            "red":     (234,  83,  39),
            "yellow":  (255, 220,  50),
            "orange":  (255, 140,   0),
            "purple":  (150,  60, 200),
            "black":   (20,   20,  20),
            "brown":   (120,  72,  40),
            "maroon":  (128,   0,   0),
            "gold":    (212, 175,  55),
            "darkred": (139,   0,   0),
            "violet":  (180,  80, 220),
            "crimson": (220,  20,  60),
            "cyan":    (0,   200, 200),
            "lime":    (160, 220,  40),
            "magenta": (220,  40, 180),
            "rainbow": (255, 255, 255),
        }

    @property
    def screen_surf(self) -> Surface:
        assert self.screen is not None
        return self.screen

    def start_pygame(self) -> None:
        """Initialize pygame, create the window, and load all image assets."""

        pygame.init()
        self.screen = pygame.display.set_mode((self.height, self.width))
        pygame.display.set_caption("Fly_in")

        self.fly_in_status = True

        raw_bg = pygame.image.load(os.path.join(
            os.path.dirname(__file__), "fundo.png"))
        self.background = pygame.transform.scale(
            raw_bg, (self.width, self.height))

        raw_start = pygame.image.load(os.path.join(
            os.path.dirname(__file__), "start.png"))
        self.start_img = pygame.transform.scale(raw_start, (80, 80))

        raw_end = pygame.image.load(os.path.join(
            os.path.dirname(__file__), "end.png"))
        self.end_img = pygame.transform.scale(raw_end, (80, 80))

        raw_drone = pygame.image.load(os.path.join(
            os.path.dirname(__file__), "drone.png"))
        self.drone_img = pygame.transform.scale(raw_drone, (80, 80))

    def limits_graph(self, ) -> None:
        """Compute the bounding box of all zone
                coordinates for coordinate conversion."""

        self.all_x: list[float] = []
        self.all_y: list[float] = []
        for zone in self.graph.zone_dict.values():
            x, y = zone.coordinates
            self.all_x.append(x)
            self.all_y.append(y)

        self.min_x = min(self.all_x)
        self.max_x = max(self.all_x)
        self.min_y = min(self.all_y)
        self.max_y = max(self.all_y)

    def _compute_margin(self) -> int:
        """Compute an appropriate margin based
                on the map coordinate spread."""

        x_spread = self.max_x - self.min_x
        y_spread = self.max_y - self.min_y
        spread = max(x_spread, y_spread)
        if spread == 0:
            return 400

        available = min(self.width, self.height)
        space_per_unit = available / (spread + 2)

        if space_per_unit < 80:
            return 50
        else:
            margin = int((available - spread * space_per_unit) / 2)
            return max(50, min(450, margin))

    def _convert_coordinates(self,
                             value_x: float,
                             value_y: float) -> tuple[float, float]:
        """Convert map grid coordinates to
                pygame screen pixel coordinates."""

        self.margin = self._compute_margin()
        range_x = self.max_x - self.min_x
        range_y = self.max_y - self.min_y

        if range_x == 0:
            range_x = 1

        pixel_x = self.margin + (value_x - self.min_x) / \
            range_x * (self.width - 2 * self.margin)

        if range_y == 0:
            pixel_y = self.height / 2
        else:
            pixel_y_inverted = self.margin + \
                (value_y - self.min_y) / range_y * \
                (self.height - 2 * self.margin)
            pixel_y = self.height - pixel_y_inverted

        return (pixel_x, pixel_y)

    def _color_zone(self, zone: Zone) -> tuple[int, int, int]:
        """Return the display color for a given zone based on its type."""

        if zone == self.graph.start_zone:
            return self.CORES["normal"]

        elif zone == self.graph.end_zone:
            return self.CORES["normal"]

        if zone.color and zone.color != "None":
            from_map = self.color_map.get(zone.color.lower())
            if from_map is not None:
                return from_map

        elif zone.type_zone == Type_zone.normal:
            return self.CORES["normal"]

        elif zone.type_zone == Type_zone.blocked:
            return self.CORES["blocked"]

        elif zone.type_zone == Type_zone.restricted:
            return self.CORES["restricted"]

        elif zone.type_zone == Type_zone.priority:
            return self.CORES["priority"]
        return (200, 200, 200)

    def _parse_history(self) -> dict[int, dict[str, str]]:
        """Parse the simulation history into
                a turn-indexed drone position map."""

        turns: dict[int, dict[str, str]] = {}

        all_drones_ids: set[str] = set()
        for line in self.history:
            for movement in line.split(" "):
                if not movement:
                    continue
                parts = movement.split("-")
                all_drones_ids.add(parts[0])

        turns[0] = {
            drone_id: self.graph.start_zone.name
            for drone_id in all_drones_ids}

        for turn_num in range(1, self.total_turns + 1):
            turns[turn_num] = dict(turns[turn_num - 1])

        for turn_idx, line in enumerate(self.history):
            turn_num = turn_idx + 1
            for movement in line.split(" "):
                if not movement:
                    continue
                parts = movement.split("-")
                drone_id = parts[0]
                zone_name = parts[-1]
                turns[turn_num][drone_id] = zone_name
                for future_turn in range(turn_num + 1, self.total_turns + 1):
                    if turns[future_turn].get(drone_id) == turns[turn_num - 1].get(drone_id):
                        turns[future_turn][drone_id] = zone_name
                    else:
                        break

        return turns

    def _draw_legend(self) -> int:
        """Draw the zone type legend in the top-right corner of the screen."""

        legend_items: list[tuple[str, tuple[int, int, int]]] = [
            ("Normal zone", self.CORES["normal"]),
            ("Blocked zone", self.CORES["blocked"]),
            ("Restricted zone", self.CORES["restricted"]),
            ("Priority zone", self.CORES["priority"]),
        ]

        has_map_colors = any(
            zone.color and zone.color != "None"
            for zone in self.graph.zone_dict.values()
            if zone != self.graph.start_zone and zone != self.graph.end_zone
        )
        if has_map_colors:
            return 20

        font = pygame.font.SysFont("Arial", 16)
        x: int = self.width - 200
        y: int = 20
        square_size: int = 16
        padding: int = 8

        for label, color in legend_items:
            pygame.draw.rect(self.screen_surf, color,
                             (x, y, square_size, square_size))
            text = font.render(label, True, (50, 50, 50))
            self.screen_surf.blit(text, (x + square_size + 6, y))
            y += square_size + padding
        return y

    def rotate_pygame(self) -> None:
        """Run the main pygame loop, rendering
                the graph and animating drones."""

        self.start_pygame()

        self.limits_graph()
        clock: pygame.time.Clock = pygame.time.Clock()
        drone_positions: dict[int, dict[str, str]] = self._parse_history()
        mode: str = "paused"

        while self.fly_in_status:
            self.screen_surf.blit(self.background, (0, 0))

            for connection in self.graph.connection_dict.values():
                zone_a = connection.zone_a
                zone_b = connection.zone_b

                pixel_start = self._convert_coordinates(
                    zone_a.coordinates[0], zone_a.coordinates[1])
                pixel_end = self._convert_coordinates(
                    zone_b.coordinates[0], zone_b.coordinates[1])

                line_color = (225, 165, 0)

                pygame.draw.line(self.screen_surf, line_color,
                                 pixel_start, pixel_end, 2)

            for zone in self.graph.zone_dict.values():
                x, y = zone.coordinates
                pixel_position = self._convert_coordinates(x, y)
                zone_radius = 15

                if zone == self.graph.start_zone:
                    rect = self.start_img.get_rect(
                        center=(int(pixel_position[0]),
                                int(pixel_position[1])))
                    self.screen_surf.blit(self.start_img, rect)

                elif zone == self.graph.end_zone:
                    rect = self.end_img.get_rect(
                        center=(int(pixel_position[0]),
                                int(pixel_position[1])))
                    self.screen_surf.blit(self.end_img, rect)

                else:
                    zone_color = self._color_zone(zone)
                    pygame.draw.circle(self.screen_surf, zone_color,
                                       pixel_position, zone_radius)

            if self.current_turn < len(drone_positions):
                font = pygame.font.SysFont("Arial", 15)
                for drone_id, zone_name in \
                        drone_positions[self.current_turn].items():
                    zone_opt = self.graph.zone_dict.get(zone_name)

                    if zone_opt is None:
                        continue

                    pixel_position = self._convert_coordinates(
                        zone_opt.coordinates[0], zone_opt.coordinates[1])
                    self.screen_surf.blit(
                        self.drone_img,
                        (pixel_position[0] - self.drone_img.get_width()
                            // 2,
                            pixel_position[1] - self.drone_img.get_height()
                            // 2)
                    )
                    text = font.render(drone_id, True, (0, 0, 0))
                    self.screen_surf.blit(text, (
                        pixel_position[0] - text.get_width()
                        // 2, + pixel_position[1] +
                        self.drone_img.get_height() // 2))

            font_mode = pygame.font.SysFont("Arial", 16)
            if mode == "paused":
                msg = [
                    "SPACE: to start",
                    "M: manual",
                    "A: auto"
                ]
            elif mode == "manual":
                msg = [
                    f"MANUAL — Turn {self.current_turn}",
                    "M: next turn",
                    "A: auto"
                ]
            else:
                msg = [
                    f"AUTO — Turn {self.current_turn}",
                    "SPACE: pause",
                    "M: manual"
                ]

            y_after_legend: int = self._draw_legend()
            x_mode: int = self.width - 200
            y_mode = y_after_legend + 10
            line_spacing: int = 24

            for line in msg:
                text_mode = font_mode.render(line, True, (50, 50, 50))
                self.screen_surf.blit(text_mode, (x_mode, y_mode))
                y_mode += line_spacing

            advance_one: bool = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.fly_in_status = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        mode = "paused" if mode == "auto" else "auto"
                    elif event.key == pygame.K_m:
                        mode = "manual"
                        advance_one = True
                    elif event.key == pygame.K_a:
                        mode = "auto"

            if mode == "auto":
                clock.tick(2)
                if self.current_turn < len(drone_positions) - 1:
                    self.current_turn += 1
            elif mode == "manual" and advance_one:
                if self.current_turn < len(drone_positions) - 1:
                    self.current_turn += 1

            pygame.display.flip()
        pygame.quit()
