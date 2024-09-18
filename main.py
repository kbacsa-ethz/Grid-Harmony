import numpy as np
import pygame
import time
from sprites import BackgroundSprite, PlantSprite, CitySprite
from geometry import segments_intersect
from camera import Camera
from constants import *
import random

pygame.init()
pygame.display.set_caption("SEC Game")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
running = True
random.seed(3)
np.random.seed(3)

clock = pygame.time.Clock()

# Create a camera instance
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

energy_options = ['oil', 'nuclear', 'solar', 'wind', 'coal', 'geothermal']
city_options = ['dense', 'sparse']
pollution_level = 0
max_pollution_level = 100  # Adjust as needed

# create world
tile_type = [EMPTY, FIELD, FOREST, LAKE, PLANT, CITY]
tile_probabilities = [0.57, 0.05, 0.05, 0.03, 0.25, 0.05]
world = np.random.choice(tile_type, size=(WORLD_WIDTH, WORLD_HEIGHT), p=tile_probabilities)
plants, cities, backgrounds = [], [], []
num_plants, num_cities = 0, 0
for i in range(WORLD_WIDTH):
    for j in range(WORLD_HEIGHT):
        if FIELD <= world[i, j] <= LAKE:
            backgrounds += [
                BackgroundSprite(world[i, j], (i * TILE_WIDTH + TILE_WIDTH // 2, j * TILE_HEIGHT + TILE_HEIGHT // 2))]
        if world[i, j] == PLANT:
            plants += [PlantSprite(random.choice(energy_options),
                                   (i * TILE_WIDTH + TILE_WIDTH // 2, j * TILE_HEIGHT + TILE_HEIGHT // 2))]
            num_plants += 1
        elif world[i, j] == CITY:
            cities += [CitySprite(random.choice(city_options),
                                  (i * TILE_WIDTH + TILE_WIDTH // 2, j * TILE_HEIGHT + TILE_HEIGHT // 2))]
            num_cities += 1

power_grid = np.zeros((num_plants, num_cities)).astype(np.bool_)
activated_plants = np.zeros(num_plants).astype(np.bool_)
powered_cities = np.zeros(num_cities).astype(np.bool_)
all_background = pygame.sprite.Group(backgrounds)
all_plants = pygame.sprite.Group(plants)
all_cities = pygame.sprite.Group(cities)

start_pos = None
end_pos = None
draw_wire = False

# Start music and load sound effects
pygame.mixer.init()
pygame.mixer.music.load("assets/music_loop.mp3")
pygame.mixer.music.play(-1)  # Loop indefinitely
pygame.mixer.music.set_volume(0.3)

activate_sound = pygame.mixer.Sound("assets/activate.wav")
disconnect_sound = pygame.mixer.Sound("assets/disconnect.wav")
power_sound = pygame.mixer.Sound("assets/connect_city.wav")
sucess_sound = pygame.mixer.Sound("assets/success.wav")
defeat_sound = pygame.mixer.Sound("assets/defeat.wav")
activate_sound.set_volume(0.5)
disconnect_sound.set_volume(0.5)
power_sound.set_volume(5.0)


class Player:
    def __init__(self, initial_money):
        self.money = initial_money


# Player
def get_name_input(screen, font):
    """Prompts the user for their name using a text input box.

    Args:
        screen: The Pygame screen to draw on.
        font: The font to use for the text.

    Returns:
        The entered name as a string.
    """

    input_box = pygame.Rect(100, 100, 140, 32)
    color_inactive = pygame.Color('lightskyblue')
    color_active = pygame.Color('dodgerblue')
    color = color_inactive
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    color = color_active
                else:
                    color = color_inactive
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:

                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        screen.fill((30, 30, 30))

        pygame.draw.rect(screen, color, input_box, 2)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        pygame.display.flip()

    return text


player = Player(random.randint(600000, 900000))  # Initial money
# name = get_name_input(screen, font)
# print(f"Welcome, {name}!")

score = 0
start_time = time.time()

leaderboard_file = "leaderboard.txt"


def load_leaderboard():
    leaderboard = []
    try:
        with open(leaderboard_file, 'r') as f:
            for line in f:
                name, score = line.strip().split(',')
                leaderboard.append((name, int(score)))
    except FileNotFoundError:
        pass
    return leaderboard


def save_leaderboard(leaderboard):
    with open(leaderboard_file, 'w') as f:
        for name, score in leaderboard:
            f.write(f"{name},{score}\n")


def build_plant(plant_type):
    # Find the plant type in energy_sources
    plant_data = next(p for p in energy_sources if p['type'] == plant_type)
    if player.money >= plant_data['fixed_cost']:
        player.money -= plant_data['fixed_cost']
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


font = pygame.font.Font(None, 36)
name = "john doe"


while running:

    clock.tick(FPS)
    score = time.time() - start_time

    # EVENT HANDLING

    # check mouse events to draw wires
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # lock/unlock plant if clicked on
            if event.button == LEFT:
                # Start drawing the line
                click_start_time = time.time()
                start_pos = event.pos
            elif event.button == SCROLL_UP:  # Mouse wheel up
                camera.update_zoom(camera.zoom_step, pygame.mouse.get_pos())
            elif event.button == SCROLL_DOWN:  # Mouse wheel down
                camera.update_zoom(-camera.zoom_step, pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
            click_duration = time.time() - click_start_time
            # Stop drawing the line and finalize it
            end_pos = event.pos
            if start_pos is None:
                start_pos = end_pos
            distance = ((end_pos[0] - start_pos[0]) ** 2 +
                        (end_pos[1] - start_pos[1]) ** 2) ** 0.5

            if draw_wire:
                draw_wire = False
            elif click_duration <= CLICK_THRESHOLD and distance < DRAG_THRESHOLD:
                for i, plant in enumerate(plants):
                    event_pos_in_mask = event.pos[0] - plant.relative_rect.x, event.pos[1] - plant.relative_rect.y
                    if plant.relative_rect.collidepoint(event.pos) and plant.mask.get_at(event_pos_in_mask):
                        activated_plants[i] = not activated_plants[i]
                        activate_sound.play()
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left mouse button is held down
                # Update the end position of the line while dragging
                end_pos = event.pos
                if not draw_wire:
                    distance = ((end_pos[0] - start_pos[0]) ** 2 +
                                (end_pos[1] - start_pos[1]) ** 2) ** 0.5
                    if distance >= DRAG_THRESHOLD:
                        draw_wire = True

    # GAME LOGIC

    # Update connections (only while mouse is used)
    if draw_wire:
        # Adding connections
        # iterate all cities for all plants. if the wire connects them and they are not already connected, then connect them
        for i, plant in enumerate(plants):
            start_pos_in_mask = start_pos[0] - plant.relative_rect.x, start_pos[1] - plant.relative_rect.y
            # check is plant is unlocked, is the click in the rectangle, is the click pixel perfect
            if activated_plants[i] and plant.relative_rect.collidepoint(start_pos) and plant.mask.get_at(
                    start_pos_in_mask):
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
                        disconnect_sound.play()

    # Remove by deactivated plant
    for i, plant in enumerate(plants):
        if not activated_plants[i]:
            power_grid[i, :] = False

    # City is powered if two or more plants are connected (TODO: will need to be changed when other mechanics are added)
    for i, city in enumerate(cities):
        previous_state = powered_cities[i]
        powered_cities[i] = np.sum(power_grid[:, i].astype(int)) >= 2
        if powered_cities[i] and not previous_state:
            power_sound.play()

    # End game
    if all(powered_cities):
        print("Congratulations! You powered all cities!")
        score = time.time() - start_time
        running = False
    elif player.money <= 0:
        score = time.time() - start_time
        print("Game over! You ran out of money.")
        running = False
    elif pollution_level >= max_pollution_level:
        score = time.time() - start_time
        print("Game over! Pollution reached the maximum level.")
        running = False

    # DRAWING

    # transfer game data to graphical component
    for i, plant in enumerate(plants):
        plant.highlighted = activated_plants[i]
    for i, city in enumerate(cities):
        city.highlighted = powered_cities[i]

    # Draw backgrounds
    screen.fill(BACKGROUND_COLOR)
    for sprite in all_background:
        # update camera
        sprite.relative_image, sprite.relative_rect = camera.apply(sprite)
        sprite.draw(screen)

    # draw current connections
    for i in range(num_plants):
        for j in range(num_cities):
            if power_grid[i, j]:
                pygame.draw.line(screen, YELLOW, plants[i].relative_rect.center, cities[j].relative_rect.center,
                                 WIRE_WIDTH)

    # Draw plant and city sprites
    for sprite in all_plants:
        # update camera
        sprite.relative_image, sprite.relative_rect = camera.apply(sprite)
        # recompute mask
        sprite.mask = pygame.mask.from_surface(sprite.relative_image)
        sprite.draw(screen)
    for sprite in all_cities:
        # update camera
        sprite.relative_image, sprite.relative_rect = camera.apply(sprite)
        # recompute mask
        sprite.mask = pygame.mask.from_surface(sprite.relative_image)
        sprite.draw(screen)

    # Draw wire
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
    pollution_level = sum(plant.pollution_factor for plant in plants if plant.highlighted)
    pollution_bar_color = "RED"
    # Display pollution level
    pollution_text = font.render(f"Pollution: {pollution_level}/{max_pollution_level}", True, pollution_bar_color)
    screen.blit(pollution_text, (10, 40))

    # Pollution bar
    pollution_bar_width = 200
    pollution_bar_height = 20

    pollution_bar_rect = pygame.Rect(10, 60, pollution_bar_width, pollution_bar_height)
    pygame.draw.rect(screen, (34, 139, 34), pollution_bar_rect)
    pollution_fill_width = int(pollution_bar_width * pollution_level / max_pollution_level)
    pygame.draw.rect(screen, pollution_bar_color, (10, 60, pollution_fill_width, pollution_bar_height))

    # update the display
    pygame.display.flip()

    # Check for high score
    # leaderboard = load_leaderboard()
    # if (name, score) not in leaderboard and len(leaderboard) < 10 or score > leaderboard[-1][1]:
    #     name = input("Enter your name: ")
    #     leaderboard.append((name, score))
    #     leaderboard.sort(key=lambda x: x[1], reverse=True)
    #     leaderboard = leaderboard[:10]
    #     save_leaderboard(leaderboard)

    # Print final score and leaderboard
    # print(f"Your final score: {score}")
    # print("Leaderboard:")
    # for name, score in leaderboard:
    #     print(f"{name}: {score}")

# End game celebration
pygame.mixer.music.stop()

if all(powered_cities):
    sucess_sound.play()
else:
    defeat_sound.play()
pygame.time.delay(5000)
pygame.quit()
