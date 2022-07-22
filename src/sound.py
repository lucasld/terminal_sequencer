import pygame


class Sound:

    def __init__(self, config):
        self.sounds = config
        # intialize mixer
        pygame.mixer.init()
        self.current_channel = 0
        self.channel_number = 500
        pygame.mixer.set_num_channels(self.channel_number)
        # load sounds
        for key, path in self.sounds.items():
            self.sounds[key] = pygame.mixer.Sound(path)
    

    def play(self, note: str, volume=1):
        self.sounds[note].set_volume(volume)
        pygame.mixer.Channel(self.current_channel).play(self.sounds[note])
        self.current_channel += 1
        if self.current_channel >= self.channel_number - 1:
            self.current_channel = 0
