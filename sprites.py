import pygame
from constants import *

class PlantSprite(pygame.sprite.Sprite):
    def __init__(self, plant_type, position):
        super().__init__()

        # Load plant image based on type
        self.plant_type = plant_type
        self.image = pygame.image.load(f'assets/{plant_type}_plant.png').convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(position)
        self.highlighted = False

        # Cost and operation data
        self.cost = self.get_cost_from_type(plant_type)
        self.operational_cost = self.get_operational_cost_from_type(plant_type)
        self.pollution_factor = self.get_pollution_factor_from_type(plant_type)

        self.relative_image = self.image
        self.relative_rect = self.rect
        self.mask = pygame.mask.from_surface(self.relative_image)

    def draw(self, surface):
        surface.blit(self.relative_image, self.relative_rect.topleft)
        if self.highlighted:
            self.draw_contour(surface)

    def draw_contour(self, surface):
        mask_outline = self.mask.outline()
        outline_color = YELLOW
        outline_width = 1
        for point in mask_outline:
            pygame.draw.circle(surface, outline_color, (self.relative_rect.x + point[0], self.relative_rect.y + point[1]), outline_width)

    def get_cost_from_type(self, plant_type):
        # Assuming cost data is stored in a dictionary in constants.py
        cost_data = next(data for data in PLANT_DATA if data['type'] == plant_type)
        return cost_data['fixed_cost']

    def get_operational_cost_from_type(self, plant_type):
        # Assuming operational cost data is stored in a dictionary in constants.py
        cost_data = next(data for data in PLANT_DATA if data['type'] == plant_type)
        return cost_data['operational_cost']

    def get_pollution_factor_from_type(self, plant_type):
        # Assuming pollution factor data is stored in a dictionary in constants.py
        cost_data = next(data for data in PLANT_DATA if data['type'] == plant_type)
        return cost_data['pollution_factor']

class PermanentWire(pygame.sprite.Sprite):
    def __init__(self, start_pos, end_pos, color=YELLOW, width=WIRE_WIDTH):
        super().__init__()
        self.image = pygame.Surface([abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1])])
        self.image.set_colorkey((0, 0, 0))  # Set transparent color
        pygame.draw.line(self.image, color, (0, 0), (self.image.get_width(), self.image.get_height()), width)
        self.rect = self.image.get_rect()
        self.rect.center = ((start_pos[0] + end_pos[0]) // 2, (start_pos[1] + end_pos[1]) // 2)
        self.angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
        self.image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):  

        # Update position or other attributes as needed
        pass
    
class CitySprite(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = pygame.image.load('assets/{}_city.png'.format(image)).convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(position)
        self.highlighted = False
        self.relative_image = self.image
        self.relative_rect = self.rect
        self.mask = pygame.mask.from_surface(self.relative_image)

    def draw(self, surface):
        surface.blit(self.relative_image, self.relative_rect.topleft)
        if self.highlighted:
            self.draw_contour(surface)

    def draw_contour(self, surface):
        mask_outline = self.mask.outline()
        outline_color = GREEN
        outline_width = 1
        for point in mask_outline:
            pygame.draw.circle(surface, outline_color, (self.relative_rect.x + point[0], self.relative_rect.y + point[1]), outline_width)