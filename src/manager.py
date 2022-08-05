import time
import yaml

from src.grid import Grid
from src.inputs import Inputs
from src.sound import Sound


class Manager:
    """Manager combines inputs (keyboard and mouse), grid displaying and sound
    playing.
    
    :param config_path: path of the config file to use, defaults to 'config.yml'
    :type config_path: string, optional"""

    def __init__(self, config_path='config.yml'):
        """Constructor function"""
        self.config_path = config_path
        self.config = self.load_config()
        self.sound_manager = Sound(self.config)
        self.grid_manager = Grid(self.config['grid'], self.sound_manager)
        self.input_manager = Inputs(self.config['keyboard'],
                                       self.grid_manager)
        

    def load_config(self) -> dict:
        """Load the project config file.
        
        :returns: dictonary containing config parameters
        :rtype: dictonary
        """
        with open(self.config_path, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc


    def start(self):
        """Run the application."""
        # starting time
        start_time = time.time()
        while not self.input_manager.esc_pressed:
            # check for mouse clicks
            self.input_manager.mouse_check()
            # current time
            current_time = time.time()
            # move runners
            self.grid_manager.move_runners(current_time)
            # draw grid if new frame is reached
            if (current_time - start_time) >= 1/self.config['frame_rate']:
                self.grid_manager.draw_grid()
                start_time = current_time

