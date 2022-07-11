import numpy as np
from pynput import keyboard
import curses
import time
import os

class Screen:
    def __init__(self, bpm=120):
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()
        self.console = curses.initscr()
        curses.start_color()
        # hyperparameters
        self.HEIGHT, self.WIDTH = self.console.getmaxyx()
        self.BPM = bpm
        self.Y, self.X = 0, 0
        # init display matrix
        self.init_screen_matrix()

    def init_screen_matrix(self):
        self.screen = np.empty((self.HEIGHT-1, self.WIDTH-1), dtype=str)
        self.screen[self.screen == ""] = '.'

    def on_press(self, key):
        global screen
        if key == key.down:
            self.move_curser((1, 0))
        elif key == key.up:
            self.move_curser((-1, 0))
        elif key == key.left:
            self.move_curser((0, -1))
        elif key == key.right:
            self.move_curser((0, 1))
    
    def on_release(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def draw_screen(self):
        self.console.erase()
        #for y,x in np.argwhere(self.screen != self.screen_new):
        #    self.console.addch(y, x, self.screen_new[y, x], curses.A_STANDOUT if y==self.Y and x==self.X else curses.COLOR_BLACK)
        for i in range(self.screen.shape[0]):
            for j in range(self.screen.shape[1]):
                self.console.addch(i, j, self.screen[i,j], curses.A_STANDOUT if i==self.Y and j==self.X else curses.COLOR_BLACK)
        self.console.refresh()

    def move_curser(self, dir: tuple) -> np.ndarray:
        ny, nx = self.Y + dir[0], self.X + dir[1]
        if 0 <= nx < self.WIDTH and 0 <= ny < self.HEIGHT:
            self.Y, self.X = ny, nx

    def update_size(self):
        if not curses.is_term_resized(self.HEIGHT, self.WIDTH):  # no need to resize
            return
        size = self.console.getmaxyx()
        x = max(size[1], 10)
        y = max(size[0], 25)
        self.WIDTH, self.HEIGHT = x, y
        # update intendations
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
                self.screen[0, -1] = 'O' if self.screen[0, -1] != 'O' else 'o'
            if i==250000:
                self.draw_screen()
                i=0


if __name__ == "__main__":
    screen = Screen()
    screen.draw()