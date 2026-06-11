from graph import Graph
from zones import Zone, Type_zone
import pygame
import os

class Visualizer:

    def __init__(self, graph: Graph, history: list[str]) -> None:
        self.graph = graph
        self.history = history

        self.height: int = 1000
        self.width: int = 1020
        self.screen = None
        self.fly_in_status = False
        self.current_turn: int = 0 
        self.CORES = {
            "normal": (0, 255, 0),
            "blocked": (255, 50, 50),
            "restricted": (0, 0, 255),
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
        self.start_img = pygame.transform.scale(raw_start, (90, 90))

        raw_end = pygame.image.load(os.path.join(os.path.dirname(__file__), "end.png"))
        self.end_img = pygame.transform.scale(raw_end, (90, 90))

        raw_drone = pygame.image.load(os.path.join(os.path.dirname(__file__), "drone.png"))
        self.drone_img = pygame.transform.scale(raw_drone, (20, 20))

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
            return self.CORES["start"]
                
        elif zone == self.graph.end_zone:
            return self.CORES["end"]
        
        elif zone.type_zone == Type_zone.normal:
            return self.CORES["normal"]
                
        elif zone.type_zone == Type_zone.blocked:
            return self.CORES["blocked"]
                
        elif zone.type_zone == Type_zone.restricted:
            return self.CORES["restricted"]
                
        elif zone.type_zone == Type_zone.priority:
            return self.CORES["priority"]

    def _parse_history(self) -> dict[int, dict[str, str]]:
        turns: dict = {}
        for turn_idx, line in enumerate(self.history):
            turns[turn_idx] = {}
            for movement in line.split(" "):
                parts = movement.split("-")
                drone_id = parts[0]
                zone_name = parts[-1]
                turns[turn_idx][drone_id] = zone_name
        return turns

    def rotate_pygame(self):
        self.start_pygame()
        self.limits_graph()
        clock = pygame.time.Clock()
        drone_positions = self._parse_history()
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
                    img_y = max(0, pixel_position[1] - self.start_img.get_height())
                    self.screen.blit(self.start_img, (img_x, img_y))
                

                elif zone == self.graph.end_zone:
                    img_x = pixel_position[0] - self.end_img.get_width() // 2
                    img_y = pixel_position[1] - self.end_img.get_height()

                    img_x = max(0, min(img_x, self.width - self.end_img.get_width()))
                    img_y = max(0, img_y)
                    self.screen.blit(self.end_img, (img_x, img_y))


                else:
                    zone_color = self._color_zone(zone)
                    pygame.draw.circle(self.screen, zone_color, pixel_position, zone_radius)
            
            if self.current_turn < len(drone_positions):
                for drone_id, zone_name in drone_positions[self.current_turn].items():
                    zone = self.graph.zone_dict.get(zone_name)
                    if zone:
                        pixel_position = self._convert_coordinates(zone.coordinates[0], zone.coordinates[1])
                    self.screen.blit(self.drone_img, (pixel_position[0] - self.drone_img.get_width() // 2, pixel_position[1] - self.drone_img.get_height() // 2))

            clock.tick(2)
            self.current_turn += 1
            if self.current_turn >= len(self.history):
                self.current_turn = 0

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.fly_in_status = False

            pygame.display.flip()
                

        pygame.quit()
