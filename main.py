import numpy as np
import pygame
from sprites import PlantSprite, CitySprite
from constants import *
import random


pygame.init()
pygame.display.set_caption("SEC Game")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
running = True
random.seed(3)

clock = pygame.time.Clock()


energy_options = ['oil', 'nuclear', 'solar']
city_options = ['dense', 'sparse']

# create plants
plants = [PlantSprite(random.choice(energy_options), 100 * 2 * i + 50, 100) for i in range(NUM_PLANTS)]
cities = [CitySprite(random.choice(city_options), 150 * 3 * i + 50, 300) for i in range(NUM_CITIES)]
power_grid = np.zeros((NUM_PLANTS, NUM_CITIES)).astype(np.bool_)

all_plants = pygame.sprite.Group(plants)
all_cities = pygame.sprite.Group(cities)

start_pos = None
end_pos = None
draw_wire = False

while running:

    clock.tick(FPS)

    # EVENT HANDLING

    # check mouse events to draw wires
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for plant in plants:
                if plant.rect.collidepoint(event.pos):
                    if plant.highlighted:
                        plant.highlighted = False
                    else:
                        plant.highlighted = True

            # Start drawing the line
            start_pos = event.pos
            draw_wire = True

        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop drawing the line and finalize it
            end_pos = event.pos
            draw_wire = False
        elif event.type == pygame.MOUSEMOTION and draw_wire:
            # Update the end position of the line while dragging
            end_pos = event.pos

    # GAME LOGIC
    if not draw_wire:
        start_pos = None
        end_pos = None

    if start_pos and end_pos:
        # iterate all cities for all plants. if the wire connects them and they are not already connected, then connect them
        for i, plant in enumerate(plants):
            start_pos_in_mask = start_pos[0] - plant.rect.x, start_pos[1] - plant.rect.y
            # second part is for pixel perfect collision
            if plant.rect.collidepoint(start_pos) and plant.mask.get_at(start_pos_in_mask):
                for j, city in enumerate(cities):
                    end_pos_in_mask = end_pos[0] - city.rect.x, end_pos[1] - city.rect.y
                    if city.rect.collidepoint(end_pos) and city.mask.get_at(end_pos_in_mask):
                        if not power_grid[i, j]:
                            power_grid[i, j] = True

    # DRAWING
    # draw
    screen.fill(BACKGROUND_COLOR)

    for i in range(NUM_PLANTS):
        for j in range(NUM_CITIES):
            if power_grid[i, j]:
                pygame.draw.line(screen, YELLOW, plants[i].rect.center, cities[j].rect.center, WIRE_WIDTH)

    all_plants.draw(screen)
    for sprite in all_plants:
        sprite.draw(screen)
    all_cities.draw(screen)
    for sprite in all_cities:
        sprite.draw(screen)

    if draw_wire:
        if start_pos and end_pos:
            pygame.draw.line(screen, YELLOW, start_pos, end_pos, WIRE_WIDTH)

    # update the display
    pygame.display.flip()
