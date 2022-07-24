import os
from os import listdir
from os.path import isfile, join
from numpy import char
import pygame


class Sound:

    def __init__(self, config):
        self.config = config
        self.sounds = config['sounds']
        self.get_sound_paths()
        # intialize mixer
        pygame.mixer.init()
        self.current_channel = 0
        self.channel_number = 500
        pygame.mixer.set_num_channels(self.channel_number)
        # load sounds
        for key, path in self.sounds.items():
            self.sounds[key] = (path, pygame.mixer.Sound(path))
    

    def get_sound_paths(self, dir='/sounds', endings=('.wav', '.mp3')):
        """Add the paths of all sounds in dir to self.sounds
        
        :param dir: directory in which to search for soundfiles
        :type dir: str
        :param endings: endings that define a soundfile
        :type endings: list/tuple of strings
        """
        path = os.path.abspath(os.getcwd()) + dir
        # iterate through all elements in path dir
        for f in listdir(path):
            joined_path = join(path, f)
            # check if path points to file
            if isfile(joined_path):
                # check if file is a soundfile
                if any(e in joined_path for e in endings):
                    # find unique identifier symbol for the new sound
                    unique_identifier = self.create_sound_identifier()
                    self.sounds[unique_identifier] = joined_path
            # go into directory and search for more soundfiles
            else:
                self.get_sound_paths(dir=join(dir, f))


    def create_sound_identifier(self) -> str:
        """Create a unique symbol that will be used to identify a sound.
        
        :returns: a unique symbol
        :rtype: str
        """
        for unicode in range(200, 100_000):
            character = chr(unicode)
            # check that character was not already chosen as sound identifier
            if character not in self.sounds.keys():
                # check that character is anywhere else as function key
                for key, value in self.config.items():
                    if type(value) == dict:
                        if character in value.values():
                            break
                    elif character == value:
                        break
                else:
                    return character

    

    def play(self, note: str, volume=1):
        self.sounds[note][1].set_volume(volume)
        pygame.mixer.Channel(self.current_channel).play(self.sounds[note][1])
        self.current_channel += 1
        if self.current_channel >= self.channel_number - 1:
            self.current_channel = 0
