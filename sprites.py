import pygame
from constants import *


class BackgroundSprite(pygame.sprite.Sprite):
    def __init__(self, background_type, position):
        super().__init__()

        # Load plant image based on type
        self.background_type = background_type
        self.image = pygame.image.load(f'assets/background_{background_type}.png').convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(position)
        self.relative_image = self.image
        self.relative_rect = self.rect

    def draw(self, surface):
        surface.blit(self.relative_image, self.relative_rect.topleft)


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