import pygame
from constants import *


class PlantSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/{}_plant.png'.format(image)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.highlighted = False
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        if self.highlighted:
            self.draw_contour(surface)

    def draw_contour(self, surface):
        mask_outline = self.mask.outline()
        outline_color = YELLOW
        outline_width = 1
        for point in mask_outline:
            pygame.draw.circle(surface, outline_color, (self.rect.x + point[0], self.rect.y + point[1]), outline_width)


class CitySprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/{}_city.png'.format(image)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
