import numpy as np
from pynput import keyboard
import curses
import time
import os

class Screen:
    def __init__(self, bpm=120):
        # init listener
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()
        # init screen
        self.console = curses.initscr()
        curses.start_color()
        # hyperparameters
        self.HEIGHT, self.WIDTH = self.console.getmaxyx()
        self.BPM = bpm
        self.Y, self.X = 0, 0
        # character symbols
        self.empty_space = '.'
        self.timeline_position = '|'
        self.note_pos = '@'
        # init display matrix
        self.init_screen_matrix()


    def init_screen_matrix(self):
        self.screen = np.empty((self.HEIGHT-1, self.WIDTH-1, 2), dtype=str)
        self.screen[self.screen == ''] = self.empty_space

    def on_press(self, key):
        if type(key) == keyboard.Key:
            if key == key.down:
                self.Y, self.X, _ = self.move_coord(self.Y, self.X, (1, 0))
            elif key == key.up:
                self.Y, self.X, _ = self.move_coord(self.Y, self.X, (-1, 0))
            elif key == key.left:
                self.Y, self.X, _ = self.move_coord(self.Y, self.X, (0, -1))
            elif key == key.right:
                self.Y, self.X, _ = self.move_coord(self.Y, self.X, (0, 1))
        elif type(key) == keyboard.KeyCode:
            if key.char == "e":
                self.screen[self.Y, self.X, 1] = self.timeline_position
            if key.char == "x":
                self.screen[self.Y, self.X, 0] = self.note_pos
        
    def on_release(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def draw_screen(self):
        self.console.erase()
        for y in range(self.screen.shape[0]):
            for x in range(self.screen.shape[1]):
                color = curses.A_STANDOUT if y==self.Y and x==self.X else curses.COLOR_BLACK
                if self.screen[y, x, 1] == self.empty_space:
                    character = self.screen[y, x, 0]
                else:
                    if self.screen[y, x, 0] == self.note_pos and self.screen[y, x, 1] == self.timeline_position: 
                        character = self.screen[y, x, 0]
                        color = curses.A_STANDOUT
                    else:
                        character = self.screen[y, x, 1]
                self.console.addch(y, x, character, color)
        self.console.refresh()

    def move_coord(self, y: int, x: int, dir: tuple) -> tuple:
        ny, nx = y + dir[0], x + dir[1]
        if 0 <= nx < self.screen.shape[1] and 0 <= ny < self.screen.shape[0]:
            return ny, nx, True
        return y, x, False

    def update_size(self):
        # check if screen size changed
        if not curses.is_term_resized(self.HEIGHT, self.WIDTH):
            return
        size = self.console.getmaxyx()
        x = max(size[1], 10)
        y = max(size[0], 25)
        self.WIDTH, self.HEIGHT = x, y
        curses.resizeterm(self.HEIGHT, self.WIDTH)
        self.init_screen_matrix()
        self.console.clear()
        self.console.refresh() 

    def draw(self):
        self.draw_screen()
        t = time.time()
        i=0
        while True:
            self.update_size()
            i+=1
            nt = time.time()
            if nt - t >= 60 / self.BPM:
                t = nt
                self.screen[0, -1, 0] = 'O' if self.screen[0, -1, 0] != 'O' else 'o'
                for y, x, z in np.argwhere(self.screen == self.timeline_position)[::-1]:
                    ny, nx, moved = self.move_coord(y, x, (0, 1))
                    self.screen[y, x, z] = self.empty_space
                    if moved:
                            self.screen[ny, nx, z] = self.timeline_position

                            
            if i==250000:
                self.draw_screen()
                i=0


if __name__ == "__main__":
    screen = Screen()
    screen.draw()