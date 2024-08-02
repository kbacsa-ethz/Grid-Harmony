import pygame
from constants import *


class PlantSprite(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = pygame.image.load('assets/{}_plant.png'.format(image)).convert_alpha()
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
        outline_color = YELLOW
        outline_width = 1
        for point in mask_outline:
            pygame.draw.circle(surface, outline_color, (self.relative_rect.x + point[0], self.relative_rect.y + point[1]), outline_width)


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
