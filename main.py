import numpy as np
import pygame
from sprites import PlantSprite, CitySprite
from geometry import segments_intersect
from camera import Camera
from constants import *
import random

pygame.init()
pygame.display.set_caption("SEC Game")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
running = True
random.seed(3)

clock = pygame.time.Clock()

# Create a camera instance
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

energy_options = ['oil', 'nuclear', 'solar']
city_options = ['dense', 'sparse']

# create plants, cities and power grid
plants = [PlantSprite(random.choice(energy_options), (100 * 2 * i + 50, 100)) for i in range(NUM_PLANTS)]
cities = [CitySprite(random.choice(city_options), (150 * 3 * i + 50, 300)) for i in range(NUM_CITIES)]


power_grid = np.zeros((NUM_PLANTS, NUM_CITIES)).astype(np.bool_)
activated_plants = np.zeros(NUM_PLANTS).astype(np.bool_)
powered_cities = np.zeros(NUM_CITIES).astype(np.bool_)
all_plants = pygame.sprite.Group(plants)
all_cities = pygame.sprite.Group(cities)

start_pos = None
end_pos = None
draw_wire = False

class Player:
    def __init__(self, initial_money):
        self.money = initial_money
        
        
# Player
player = Player(1000)  # Initial money

# ... rest of the code ...

def build_plant(plant_type):
    # Find the plant type in energy_sources
    plant_data = next(p for p in energy_sources if p['type'] == plant_type)
    if player.money >= plant_data['fixed_cost']:
        player.money -= plant_data['fixed_cost']
        # Create a new plant instance
        # ...
    else:
        print("Insufficient funds")

def calculate_turn_costs():
    total_operational_cost = 0
    for plant in plants:
        total_operational_cost += plant.operational_cost
    player.money -= total_operational_cost

def calculate_income():
    income = sum(powered_cities) * 10  # Simple income model
    player.money += income


while running:

    clock.tick(FPS)

    # EVENT HANDLING

    # check mouse events to draw wires
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # lock/unlock plant if clicked on
            if event.button == LEFT:
                for i, plant in enumerate(plants):
                    event_pos_in_mask = event.pos[0] - plant.relative_rect.x, event.pos[1] - plant.relative_rect.y
                    if plant.relative_rect.collidepoint(event.pos) and plant.mask.get_at(event_pos_in_mask):
                        activated_plants[i] = not activated_plants[i]
                # Start drawing the line
                start_pos = event.pos
                draw_wire = True
            elif event.button == 4:  # Mouse wheel up
                camera.update_zoom(camera.zoom_step, pygame.mouse.get_pos())
            elif event.button == 5:  # Mouse wheel down
                camera.update_zoom(-camera.zoom_step, pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
            # Stop drawing the line and finalize it
            end_pos = event.pos
            draw_wire = False
        elif event.type == pygame.MOUSEMOTION and draw_wire:
            # Update the end position of the line while dragging
            end_pos = event.pos

    # GAME LOGIC

    # prevent point to carry over
    if not draw_wire:
        start_pos = None
        end_pos = None

    # Update connnections (only while mouse is used)
    if start_pos and end_pos:
        # Adding connections
        # iterate all cities for all plants. if the wire connects them and they are not already connected, then connect them
        for i, plant in enumerate(plants):
            start_pos_in_mask = start_pos[0] - plant.relative_rect.x, start_pos[1] - plant.relative_rect.y
            # check is plant is unlocked, is the click in the rectangle, is the click pixel perfect
            if activated_plants[i] and plant.relative_rect.collidepoint(start_pos) and plant.mask.get_at(start_pos_in_mask):
                for j, city in enumerate(cities):
                    end_pos_in_mask = end_pos[0] - city.relative_rect.x, end_pos[1] - city.relative_rect.y
                    if city.relative_rect.collidepoint(end_pos) and city.mask.get_at(end_pos_in_mask):
                        if not power_grid[i, j]:
                            power_grid[i, j] = True

        # Removing connections
        for i, plant in enumerate(plants):
            # Remove by cutting the wire
            for j, city in enumerate(cities):
                if power_grid[i, j]:
                    if segments_intersect(plant.relative_rect.center, city.relative_rect.center, start_pos, end_pos):
                        power_grid[i, j] = False

    # Remove by deactivated plant
    for i, plant in enumerate(plants):
        if not activated_plants[i]:
            power_grid[i, :] = False

    # City is powered if two or more plants are connected (TODO: will need to be changed when other mechanics are added)
    for i, city in enumerate(cities):
        powered_cities[i] = np.sum(power_grid[:, i].astype(int)) >= 2

    # DRAWING

    # transfer game data to graphical component
    for i, plant in enumerate(plants):
        plant.highlighted = activated_plants[i]
    for i, city in enumerate(cities):
        city.highlighted = powered_cities[i]

    # draw
    screen.fill(BACKGROUND_COLOR)


    for i in range(NUM_PLANTS):
        for j in range(NUM_CITIES):
            if power_grid[i, j]:
                pygame.draw.line(screen, YELLOW, plants[i].relative_rect.center, cities[j].relative_rect.center, WIRE_WIDTH)

    #all_plants.draw(screen)
    for sprite in all_plants:
        # update camera
        sprite.relative_image, sprite.relative_rect = camera.apply(sprite)
        # recompute mask
        sprite.mask = pygame.mask.from_surface(sprite.relative_image)
        sprite.draw(screen)
    #all_cities.draw(screen)
    for sprite in all_cities:
        # update camera
        sprite.relative_image, sprite.relative_rect = camera.apply(sprite)
        # recompute mask
        sprite.mask = pygame.mask.from_surface(sprite.relative_image)
        sprite.draw(screen)

    if draw_wire:
        if start_pos and end_pos:
            pygame.draw.line(screen, YELLOW, start_pos, end_pos, WIRE_WIDTH)
    calculate_turn_costs()
    calculate_income()
    # ...

    # Display money
    font = pygame.font.Font(None, 36)
    money_text = font.render(f"Money: {player.money}", True, (0, 0, 0))
    screen.blit(money_text, (10, 10))

    # update the display
    pygame.display.flip()
