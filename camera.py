import pygame


class Camera:
    def __init__(self, width, height):
        self.zoom_level = 1.0
        self.zoom_step = 0.05
        self.width = width
        self.height = height
        self.offset = pygame.Vector2(0, 0)

    def apply(self, entity):
        zoomed_width = int(entity.rect.width * self.zoom_level)
        zoomed_height = int(entity.rect.height * self.zoom_level)
        zoomed_image = pygame.transform.scale(entity.image, (zoomed_width, zoomed_height))
        zoomed_rect = zoomed_image.get_rect(center=(entity.position + self.offset) * self.zoom_level)
        return zoomed_image, zoomed_rect

    def update_zoom(self, zoom_increment, mouse_pos):
        old_zoom_level = self.zoom_level
        self.zoom_level += zoom_increment
        if self.zoom_level < self.zoom_step:
            self.zoom_level = self.zoom_step

        # Calculate the new offset to keep the mouse position as the focal point
        mx, my = mouse_pos
        mx /= old_zoom_level
        my /= old_zoom_level
        self.offset.x -= mx * (self.zoom_level - old_zoom_level)
        self.offset.y -= my * (self.zoom_level - old_zoom_level)
