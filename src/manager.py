import time
import yaml

from src.grid import Grid
from src.keyboard import Keyboard
from src.sound import Sound


class Manager:

    def __init__(self, config_path="config.yml"):
        self.config = self.load_config(config_path)
        self.sound_manager = Sound(self.config['sounds'])
        self.grid_manager = Grid(self.config['grid'], self.sound_manager)
        self.keyboard_manager = Keyboard(self.config['keyboard'], self.grid_manager)
        

    def load_config(self, path: str) -> dict:
        with open(path, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc


    def start(self):
        # starting time
        start_time = time.time()
        while True:
            # current time
            current_time = time.time()
            # move runners
            self.grid_manager.move_runners(current_time)
            # draw grid if new frame is reached
            if (current_time - start_time) >= 1/self.config['frame_rate']:
                self.grid_manager.draw_grid()
                start_time = current_time

