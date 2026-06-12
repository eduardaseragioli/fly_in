from graph import Graph
from zones import Zone, Type_zone
import pygame
import os

class Visualizer:

    def __init__(self, graph: Graph, history: list[str]) -> None:
        self.graph = graph
        self.history = history

        self.height: int = 1000
        self.width: int = 1000
        self.screen = None
        self.fly_in_status = False
        self.current_turn: int = 0
        self.CORES = {
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

    def start_pygame(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((self.height, self.width))
        pygame.display.set_caption("Fly_in")

        self.fly_in_status = True

        raw_bg = pygame.image.load(os.path.join(os.path.dirname(__file__), "fundo.png"))
        self.background = pygame.transform.scale(raw_bg, (self.width, self.height))

        raw_start = pygame.image.load(os.path.join(os.path.dirname(__file__), "start.png"))
        self.start_img = pygame.transform.scale(raw_start, (120, 120))

        raw_end = pygame.image.load(os.path.join(os.path.dirname(__file__), "end.png"))
        self.end_img = pygame.transform.scale(raw_end, (120, 120))

        raw_drone = pygame.image.load(os.path.join(os.path.dirname(__file__), "drone.png"))
        self.drone_img = pygame.transform.scale(raw_drone, (80, 80))

    def limits_graph(self, ) -> None:
        self.all_x: list = []
        self.all_y: list = []
        for zone in self.graph.zone_dict.values():
            x, y = zone.coordinates
            self.all_x.append(x)
            self.all_y.append(y)

        self.min_x = min(self.all_x)
        self.max_x = max(self.all_x)
        self.min_y = min(self.all_y)
        self.max_y = max(self.all_y)

    def _convert_coordinates(self, value_x, value_y) -> tuple:

        self.margin = 50

        try:            
            pixel_x = self.margin + (value_x - self.min_x) / (self.max_x - self.min_x) * (self.width - 2 * self.margin)
            pixel_y_inverted = self.margin + (value_y - self.min_y) / (self.max_y - self.min_y) * (self.height - 2 * self.margin)
            pixel_y = self.height - pixel_y_inverted
        except ZeroDivisionError:
            pixel_x = self.margin + (value_x - self.min_x) * (self.width - 2 * self.margin) if self.max_x != self.min_x else self.width // 2
            pixel_y = self.height // 2


        return (pixel_x, pixel_y)

    def _color_zone(self, zone: Zone):
        if zone == self.graph.start_zone:
            return self.CORES["normal"]
                
        elif zone == self.graph.end_zone:
            return self.CORES["normal"]
        
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
        turns: dict = {}

        all_drones_ids = set()
        for line in self.history:
            for movement in line.split(" "):
                parts = movement.split("-")
                all_drones_ids.add(parts[0])

        turns[0] = {drone_id: self.graph.start_zone.name for drone_id in all_drones_ids}

        for turn_idx, line in enumerate(self.history):
            turns[turn_idx + 1] = {}
            for movement in line.split(" "):
                parts = movement.split("-")
                drone_id = parts[0]
                zone_name = parts[-1]
                turns[turn_idx + 1][drone_id] = zone_name
        return turns

    def _draw_legend(self) -> None:
        legend_items = [
            ("Normal zone", self.CORES["normal"]),
            ("Blocked zone", self.CORES["blocked"]),
            ("Restricted zone", self.CORES["restricted"]),
            ("Priority zone", self.CORES["priority"]),
        ]
        font = pygame.font.SysFont("Arial", 16)
        x = self.width - 200
        y = 20
        square_size = 16
        padding = 8

        for label, color in legend_items:
            pygame.draw.rect(self.screen, color, (x, y, square_size, square_size))
            text = font.render(label, True, (50, 50, 50))
            self.screen.blit(text, (x + square_size + 6, y))
            y += square_size + padding
        return y

    def rotate_pygame(self):
        self.start_pygame()
        self.limits_graph()
        clock = pygame.time.Clock()
        drone_positions = self._parse_history()
        mode = "paused"

        while self.fly_in_status:
            self.screen.blit(self.background, (0, 0))

            for connection in self.graph.connection_dict.values():
                zone_a = connection.zone_a
                zone_b = connection.zone_b

                pixel_start = self._convert_coordinates(zone_a.coordinates[0], zone_a.coordinates[1])
                pixel_end = self._convert_coordinates(zone_b.coordinates[0], zone_b.coordinates[1])

                line_color = (225, 165, 0)

                pygame.draw.line(self.screen, line_color, pixel_start, pixel_end, 2)

            for zone in self.graph.zone_dict.values():
                x, y = zone.coordinates
                pixel_position = self._convert_coordinates(x, y)
                zone_radius = 15


                if zone == self.graph.start_zone:
                    img_x = max(0, pixel_position[0] - self.start_img.get_width() // 2)
                    img_y = max(0, pixel_position[1] - self.start_img.get_height() // 2)
                    self.screen.blit(self.start_img, (img_x, img_y))
                

                elif zone == self.graph.end_zone:
                    img_x = pixel_position[0] - self.end_img.get_width() // 2
                    img_y = pixel_position[1] - self.end_img.get_height() // 2

                    img_x = max(0, min(img_x, self.width - self.end_img.get_width()))
                    img_y = max(0, img_y)
                    self.screen.blit(self.end_img, (img_x, img_y))


                else:
                    zone_color = self._color_zone(zone)
                    pygame.draw.circle(self.screen, zone_color, pixel_position, zone_radius)
            
            if self.current_turn < len(drone_positions):
                font = pygame.font.SysFont("Arial", 15)
                for drone_id, zone_name in drone_positions[self.current_turn].items():
                    zone = self.graph.zone_dict.get(zone_name)
                    if zone:
                        pixel_position = self._convert_coordinates(zone.coordinates[0], zone.coordinates[1])
                        self.screen.blit(self.drone_img, (pixel_position[0] - self.drone_img.get_width() // 2, pixel_position[1] - self.drone_img.get_height() // 2))
                        text = font.render(drone_id, True, (0, 0, 0))
                        self.screen.blit(text, (pixel_position[0] - text.get_width() // 2, pixel_position[1] + self.drone_img.get_height() // 2))

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
            
            y_after_legend = self._draw_legend()
            x_mode = self.width - 200
            y_mode = y_after_legend + 10
            line_spacing = 24

            for line in msg:
                text_mode = font_mode.render(line, True, (50, 50, 50))
                self.screen.blit(text_mode, (x_mode, y_mode))
                y_mode += line_spacing

            self._draw_legend()

            advance_one = False
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
                self.current_turn += 1
                if self.current_turn >= len(self.history):
                    self.current_turn = 0
            elif mode == "manual" and advance_one:
                self.current_turn += 1
                if self.current_turn >= len(self.history):
                    self.current_turn = 0

            pygame.display.flip()
        pygame.quit()
