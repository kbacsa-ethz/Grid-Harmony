SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1500
PLANT_HEIGHT = 50
PLANT_WIDTH = 50
FPS = 60
BACKGROUND_COLOR = (190, 255, 50)
PLANT_COLOR = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
WIRE_WIDTH = 5

# Button constants
LEFT = 1
SCROLL_UP = 4
SCROLL_DOWN = 5
CLICK_THRESHOLD = 0.2  # 200 ms for a short click
DRAG_THRESHOLD = 10  # drag must be at least 10 pixels

# tile constants
EMPTY = 0
FIELD = 1
FOREST = 2
LAKE = 3
PLANT = 4
CITY = 5
TILE_WIDTH = 160
TILE_HEIGHT = 160
WORLD_WIDTH = 10
WORLD_HEIGHT = 10

# Plant data
PLANT_DATA = [
    {'type': 'oil', 'fixed_cost': 100, 'operational_cost': 10},
    {'type': 'nuclear', 'fixed_cost': 200, 'operational_cost': 5},
    {'type': 'solar', 'fixed_cost': 150, 'operational_cost': 0},
    {'type': 'wind', 'fixed_cost': 150, 'operational_cost': 0},
    {'type': 'coal', 'fixed_cost': 150, 'operational_cost': 0},
    {'type': 'geothermal', 'fixed_cost': 150, 'operational_cost': 0}
]
