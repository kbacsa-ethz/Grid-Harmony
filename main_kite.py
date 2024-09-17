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
        

class PlayScreen(Screen):
    grid_size = (20, 20)  # Adjust grid size as needed

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)
        self.music = None
        self.button_click_sound = SoundLoader.load('button_click.mp3')
        image = Image(source='menu_image.jpg', size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}, allow_stretch=True, keep_ratio=False)
        self.add_widget(image)
        
        # Random starting amount for the player
        self.player_budget = random.randint(1000, 5000)  # Example range for starting budget
        self.total_pollution = 0
        
        # Layout for buttons and information display
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        #back_button = Button(text='Back', size_hint=(0.15, 0.2), pos_hint={'x': 0, 'top': 1})
        #back_button.bind(on_press=self.on_back)
        #layout.add_widget(back_button)

        # Create labels for budget and pollution display
        self.budget_label = Label(text=f"Budget: ${self.player_budget}", size_hint=(1, 0.1))
        self.pollution_label = Label(text=f"Total Pollution: {self.total_pollution} units", size_hint=(1, 0.1))
        layout.add_widget(self.budget_label)
        layout.add_widget(self.pollution_label)
        
        self.add_widget(layout)
        
        # Add city and plants
        self.create_game_elements()

    def create_game_elements(self):
        # Randomly select plants for the player
        selected_plants = random.sample(PLANT_DATA, k=6)  # Randomly choose 3 plants for the player
        city_image = self.add_random_element('assets/dense_city.png')
        #self.cities.append(city_image)
        city_image = self.add_random_element('assets/sparse_city.png')
        #self.cities.append(city_image)
        for plant in selected_plants:
            plant_image = self.add_random_element(f'assets/{plant["type"]}_plant.png')
            self.update_cost_and_pollution(plant)

    def add_random_element(self, image_source):
        # Create a random position for the element
        random_x = random.uniform(0, 1)  # Random x position (normalized between 0 and 1)
        random_y = random.uniform(0, 1)  # Random y position (normalized between 0 and 1)

        element = Image(source=image_source, size_hint=(0.1, 0.1), pos_hint={'center_x': random_x, 'center_y': random_y})
        self.add_widget(element)
        return element

    def update_cost_and_pollution(self, plant):
        # Deduct fixed and operational costs from the player's budget
        self.player_budget -= plant['fixed_cost']
        self.player_budget -= plant['operational_cost']
        
        # Add to total pollution
        self.total_pollution += plant['pollution_factor']
        
        # Update labels
        self.budget_label.text = f"Budget: ${self.player_budget}"
        self.pollution_label.text = f"Total Pollution: {self.total_pollution} units"


    # def create_game_elements(self):
    #     self.grid = [[None for _ in range(self.grid_size[1])] for _ in range(self.grid_size[0])]
    #     num_cities = 3
    #     num_plants = 10

    #     # Generate cities
    #     for _ in range(num_cities):
    #         x, y = self.generate_random_position()
    #         if self.grid[x][y] is None:
    #             city = City()
    #             city.pos_hint = {"center_x": x / self.grid_size[0], "center_y": y / self.grid_size[1]}
    #             self.add_widget(city)  # Ensure city is added to the layout
    #             self.grid[x][y] = city
    #             self.cities.append(city)

    #     # Generate plants, ensuring no overlaps with cities
    #     for _ in range(num_plants):
    #         x, y = self.generate_random_position()
    #         if self.grid[x][y] is None:
    #             plant = Plant('solar')  # Specify a valid plant type
    #             plant.pos_hint = {"center_x": x / self.grid_size[0], "center_y": y / self.grid_size[1]}
    #             self.add_widget(plant)  # Ensure plant is added to the layout
    #             self.grid[x][y] = plant
    #             self.plants.append(plant)

    # def generate_random_position(self):
    #     x = random.randint(0, self.grid_size[0] - 1)
    #     y = random.randint(0, self.grid_size[1] - 1)
        #return x, y
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

    def play_button_sound(self, instance):
        if self.button_click_sound:
            self.button_click_sound.play()
    def normalize_pressure(self, pressure):
        print(pressure)
        # this might mean we are on a device whose pressure value is
        # incorrectly reported by SDL2, like recent iOS devices.
        if pressure == 0.0:
            return 1
        return dp(pressure * 10)

    def on_touch_down(self, touch):
        win = self.get_parent_window()
        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        pointsize = 2
        #print(touch.profile)
        if 'pressure' in touch.profile:
            ud['pressure'] = touch.pressure
            pointsize = self.normalize_pressure(touch.pressure)
        ud['color'] = 0.2555

        with self.canvas:
            Color(ud['color'], 1, 1, mode='hsv', group=g)
            ud['lines'] = [
                Rectangle(pos=(touch.x, 0), size=(1, win.height), group=g),
                Rectangle(pos=(0, touch.y), size=(win.width, 1), group=g),
                Point(points=(touch.x, touch.y), source='transmission.png',
                      pointsize=pointsize, group=g)]

        ud['label'] = Label(size_hint=(None, None))
        #self.update_touch_label(ud['label'], touch)
        self.add_widget(ud['label'])
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        ud = touch.ud
        ud['lines'][0].pos = touch.x, 0
        ud['lines'][1].pos = 0, touch.y

        index = -1

        while True:
            try:
                points = ud['lines'][index].points
                oldx, oldy = points[-2], points[-1]
                break
            except IndexError:
                index -= 1

        points = calculate_points(oldx, oldy, touch.x, touch.y)

        # if pressure changed create a new point instruction
        if 'pressure' in ud:
            old_pressure = ud['pressure']
            if (
                not old_pressure
                or not .99 < (touch.pressure / old_pressure) < 1.01
            ):
                g = ud['group']
                pointsize = self.normalize_pressure(touch.pressure)
                with self.canvas:
                    Color(ud['color'], 1, 1, mode='hsv', group=g)
                    ud['lines'].append(
                        Point(points=(), source='transmission.png',
                              pointsize=pointsize, group=g))

        if points:
            try:
                lp = ud['lines'][-1].add_point
                for idx in range(0, len(points), 2):
                    lp(points[idx], points[idx + 1])
            except GraphicException:
                pass

        ud['label'].pos = touch.pos
        import time
        t = int(time.time())
        if t not in ud:
            ud[t] = 1
        else:
            ud[t] += 1
        #self.update_touch_label(ud['label'], touch)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        ud = touch.ud
        self.canvas.remove_group(ud['group'])
        self.remove_widget(ud['label'])

    def update_touch_label(self, label, touch):
        label.text = 'ID: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20
    
    def complete(self, instance):
        # Stop the music
        # Make small popup that says "Congratulations! You have completed the level!"
        complete_popup = CompletePopup()
        complete_popup.open()

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
