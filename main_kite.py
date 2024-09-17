from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.audio import SoundLoader
from kivy.utils import get_color_from_hex
from kivy.graphics.texture import Texture
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Point, GraphicException
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.graphics import Rectangle, Color  # potential use for highlighting
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Line
from kivy.animation import Animation
import cv2
import numpy as np
from math import sqrt
import random 




# Assuming constants.py defines data structures like PLANT_DATA
from constants import PLANT_DATA

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.music = None
        self.button_click_sound = SoundLoader.load('button_click.mp3')

        layout = FloatLayout()
        Window.size = (600, 800)

        # Image
        image = Image(source='menu_image.jpg', size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}, allow_stretch=True, keep_ratio=False)
        layout.add_widget(image)

        # Decorate Play button
        play_button = Button(text='Start', size_hint=(None, None), size=(250, 50),
                             pos_hint={'center_x': 0.5, 'center_y': 0.35},
                             background_color=(0, 0.5, 1, 1), font_size=24, color=(1, 1, 1, 1))
        play_button.bind(on_release=self.go_to_levels)
        play_button.bind(on_press=self.play_button_sound)
        layout.add_widget(play_button)

        #Decorate Credits button
        credits_button = Button(text='Credits', size_hint=(None, None), size=(100, 50),
                                pos_hint={'x': 0.02, 'y': 0.02},
                                background_color=(0, 0.5, 1, 1), font_size=14, color=(1, 1, 1, 1))
        credits_button.bind(on_release=self.show_credits)
        credits_button.bind(on_press=self.play_button_sound)
        layout.add_widget(credits_button)

        # Decorate Instruction button
        instruction_button = Button(text='Instructions', size_hint=(None, None), size=(100, 50),
                                    pos_hint={'center_x': 0.5, 'y': 0.02},
                                    background_color=(0, 0.5, 1, 1), font_size=14, color=(1, 1, 1, 1))
        instruction_button.bind(on_release=self.show_instruction)
        instruction_button.bind(on_press=self.play_button_sound)
        layout.add_widget(instruction_button)

        # Decorate Contact us button
        contact_button = Button(text='Contact us', size_hint=(None, None), size=(100, 50),
                                pos_hint={'right': 0.98, 'y': 0.02},
                                background_color=(0, 0.5, 1, 1), font_size=14, color=(1, 1, 1, 1))
        contact_button.bind(on_release=self.show_contact)
        contact_button.bind(on_press=self.play_button_sound)
        layout.add_widget(contact_button)

        self.add_widget(layout)

    def on_enter(self, *args):
        self.play_music('game_music.mp3')

    def on_leave(self, *args):
        self.stop_music()

    def play_music(self, filename):
        self.music = SoundLoader.load(filename)
        if self.music:
            self.music.loop = True
            self.music.play()

    def stop_music(self):
        if self.music:
            self.music.stop()
            self.music.unload()

    def play_button_sound(self, instance):
        if self.button_click_sound:
            self.button_click_sound.play()

    def go_to_levels(self, instance):
        self.manager.current = 'levels'

    def show_popup(self, title, text):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scrollview = ScrollView(size_hint=(1, None), size=(Window.width * 0.8, Window.height * 0.6))
        
        text_label = Label(text=text, size_hint_y=None, height=Window.height * 0.6)
        text_label.bind(texture_size=text_label.setter('size'))
        
        scrollview.add_widget(text_label)
        content.add_widget(scrollview)

        close_button = Button(text='Close', size_hint=(None, None), size=(100, 50),
                              background_color=(1, 0, 0, 1), font_size=14, color=(1, 1, 1, 1))
        content.add_widget(close_button)

        popup = Popup(title=title, content=content, size_hint=(0.8, 0.8))
        close_button.bind(on_release=popup.dismiss)
        close_button.bind(on_release=self.play_button_sound)
        popup.open()

    def show_credits(self, instance):
        self.show_popup('Credits', 'One and a half-Indians Team')

    def show_instruction(self, instance):
        self.show_popup('Instruction', '''
  @Kiran and me writing some useful stuff here,
  which we will completely forget I guess.
''')

    def show_contact(self, instance):
        self.show_popup('Contact Us', '''
    someonesemail@ethz.ch
                        ''')

def calculate_points(x1, y1, x2, y2, steps=5):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps:
        return
    o = []
    m = dist / steps
    for i in range(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o

class CompletePopup(Popup):
    def __init__(self, **kwargs):
        super(CompletePopup, self).__init__(**kwargs)
        self.title = 'Completed!'
        self.content = Label(text='Level Complete!')
        self.size_hint = (0.5, 0.5)
        self.auto_dismiss = True

class CustomProgressBar(ProgressBar):
    def __init__(self, **kwargs):
        super(CustomProgressBar, self).__init__(**kwargs)
        with self.canvas.before:
            self.bg = Rectangle(source='assets/gauge.png', size=self.size, pos=self.pos)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

class SmokeEffect(Widget):
    def __init__(self, **kwargs):
        super(SmokeEffect, self).__init__(**kwargs)
        self.smoke_opacity = 0

        with self.canvas:
            self.smoke_image = Image(source='assets/smoke.png', size_hint=(1, 1), opacity=self.smoke_opacity)

    def update_smoke_intensity(self, intensity):
        self.smoke_opacity = intensity

    def animate(self):
        # Animate smoke opacity and movement if desired
        anim = Animation(opacity=self.smoke_opacity, duration=1)
        anim.start(self.smoke_image)       

class PlayScreen(Screen):

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        self.music = None
        self.button_click_sound = SoundLoader.load('button_click.mp3')
        image = Image(source='menu_image.jpg', size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}, allow_stretch=True, keep_ratio=False)
        self.add_widget(image)
        
        # Random starting amount for the player
        self.player_budget = random.randint(1000, 5000)
        self.total_pollution = 0
        self.max_pollution = 100  # Maximum pollution (used for the pollution gauge)
        
        # Layout for buttons and information display
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Create labels for budget and pollution display
        self.budget_label = Label(text=f"Budget: ${self.player_budget}", size_hint=(1, 0.1))
        self.pollution_label = Label(text=f"Total Pollution: {self.total_pollution} units", size_hint=(1, 0.1))
        layout.add_widget(self.budget_label)
        layout.add_widget(self.pollution_label)
        
        # Pollution Gauge
        self.pollution_gauge = CustomProgressBar(max=self.max_pollution, value=self.total_pollution, size_hint=(1, 0.1))
        layout.add_widget(self.pollution_gauge)
        
        self.add_widget(layout)

        # Add cities and plants
        self.cities = []
        self.plants = []
        self.active_connections = []  # Stores active connections between cities and plants
        self.create_game_elements()

        # Variables to track touch interaction
        self.selected_city = None
        self.current_line = None

    def create_game_elements(self):
        # Randomly select plants for the player
        selected_plants = random.sample(PLANT_DATA, k=6)
        # Add cities
        city_1 = self.add_random_element('assets/dense_city.png', is_city=True)
        city_2 = self.add_random_element('assets/sparse_city.png', is_city=True)
        self.cities.extend([city_1, city_2])

        for plant in selected_plants:
            plant_image = self.add_random_element(f'assets/{plant["type"]}_plant.png', is_city=False)
            self.plants.append((plant_image, plant))  # Store the plant image and its data

    def add_random_element(self, image_source, is_city):
        # Create a random position for the element
        random_x = random.uniform(0.2, 0.9)  # Random x position (normalized between 0.2 and 0.9)
        random_y = random.uniform(0.2, 0.9)  # Random y position (normalized between 0.2 and 0.9)

        element = Image(source=image_source, size_hint=(0.1, 0.1), pos_hint={'center_x': random_x, 'center_y': random_y})
        self.add_widget(element)
        if is_city:
            element.is_city = True
        else:
            element.is_city = False
        return element

    def on_touch_down(self, touch):
        # Check if user is selecting a city to start drawing a line
        for city in self.cities:
            if self.is_touch_in_widget(touch, city):
                self.selected_city = city
                with self.canvas:
                    Color(1, 1, 0, 1)  # Yellow wire color
                    self.current_line = Line(points=[touch.x, touch.y], width=2)

    def on_touch_move(self, touch):
        if self.selected_city and self.current_line:
            self.current_line.points += [touch.x, touch.y]

    def on_touch_up(self, touch):
        if self.selected_city and self.current_line:
            # Check if the touch ended on a plant (to finalize the connection)
            for plant, plant_data in self.plants:
                if self.is_touch_in_widget(touch, plant):
                    # Draw final wire and update cost/pollution
                    self.finalize_connection(self.selected_city, plant, plant_data)
                    break
            # Remove the temporary line
            self.canvas.remove(self.current_line)
            # Reset the drawing state
            self.selected_city = None
            self.current_line = None

    def finalize_connection(self, city, plant, plant_data):
        # Draw permanent line from city to plant
        with self.canvas:
            Color(1, 1, 0, 1)  # Yellow wire color
            city_pos = city.pos_hint
            plant_pos = plant.pos_hint
            Line(points=[
                self.width * city_pos['center_x'], self.height * city_pos['center_y'],
                self.width * plant_pos['center_x'], self.height * plant_pos['center_y']
            ], width=2)

        # Add the connection to active connections
        self.active_connections.append((city, plant))

        # Update pollution and cost
        self.update_cost_and_pollution(plant_data)

    def update_cost_and_pollution(self, plant):
        # Deduct fixed and operational costs from the player's budget
        self.player_budget -= plant['fixed_cost']
        self.player_budget -= plant['operational_cost']
        
        # Add to total pollution
        self.total_pollution += plant['pollution_factor']
        
        # Update labels and gauge
        self.budget_label.text = f"Budget: ${self.player_budget}"
        self.pollution_label.text = f"Total Pollution: {self.total_pollution} units"
        self.pollution_gauge.value = self.total_pollution

    def is_touch_in_widget(self, touch, widget):
        # Check if a touch event is inside a widget's bounds
        widget_pos = widget.pos_hint
        widget_x = self.width * widget_pos['center_x']
        widget_y = self.height * widget_pos['center_y']
        widget_width = widget.size_hint[0] * self.width
        widget_height = widget.size_hint[1] * self.height

        if (widget_x - widget_width / 2 <= touch.x <= widget_x + widget_width / 2 and
            widget_y - widget_height / 2 <= touch.y <= widget_y + widget_height / 2):
            return True
        return False
    
    def update_smoke_effect(self):
        # Adjust the smoke intensity based on the pollution
        self.smoke.update_smoke_intensity(self.total_pollution / self.max_pollution)

    def update_smoke(self, dt):
        # Update the smoke animation over time
        self.smoke.animate()
        
        
    def on_enter(self, *args):
        self.play_music('assets/music_loop.mp3')

    def on_leave(self, *args):
        self.stop_music()

    def play_music(self, filename):
        self.music = SoundLoader.load(filename)
        if self.music:
            self.music.loop = True
            self.music.play()

    def stop_music(self):
        if self.music:
            self.music.stop()
            self.music.unload()


    def on_back(self, instance):
        self.manager.current = 'menu'

class gridHarmony(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(PlayScreen(name='levels'))
        #sm.add_widget(ColoringApp(name='game'))
        return sm

if __name__ == '__main__':
    gridHarmony().run()
