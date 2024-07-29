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
plants = [PlantSprite(random.choice(energy_options), 100 * 2 * i + 50, 100) for i in range(5)]
city = [CitySprite(random.choice(city_options), 150 * 3 * i + 50, 300) for i in range(3)]

all_plants = pygame.sprite.Group(plants)
all_cities = pygame.sprite.Group(city)

wires = []
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
    # Add game logic here


    # DRAWING
    # draw
    screen.fill(BACKGROUND_COLOR)

    all_plants.draw(screen)
    for sprite in all_plants:
        sprite.draw(screen)
    all_cities.draw(screen)
    for sprite in all_cities:
        sprite.draw(screen)

    if start_pos and end_pos:
        pygame.draw.line(screen, YELLOW, start_pos, end_pos, WIRE_WIDTH)

    # update the display
    pygame.display.flip()
