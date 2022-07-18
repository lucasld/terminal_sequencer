import numpy as np
from pynput import keyboard
import curses
import time
import pygame
import configparser


class Grid:
    def __init__(self, bpm=120):
        # init listener
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()
        # init screen
        self.console = curses.initscr()
        curses.start_color()
        # parameters
        self.HEIGHT, self.WIDTH = self.console.getmaxyx()
        self.BPM = bpm  # global bpm
        self.Y, self.X = 0, 0  # y and x position of the selector
        # character symbols
        self.empty_space_chr = '.'
        self.runner_chr = '|'
        self.note_chr = '@'
        self.loop_begin_chr = '['
        self.loop_end_chr = ']'
        # keys
        self.set_runner = '0'
        self.set_note = 'x'
        self.loop_begin = '['
        self.loop_end = ']'
        # init display matrix
        self.init_screen_matrix()
        # save bpms as keys and as items the corresponding rows, time
        self.bpms = {self.BPM:[list(range(self.screen.shape[0])), 0]}
        pygame.mixer.init()
        self.current_channel = 0
        self.channel_number = 500
        pygame.mixer.set_num_channels(self.channel_number)
        self.sound = pygame.mixer.Sound("sound.mp3")
        config = configparser.ConfigParser()
        config.read('config.txt')
        self.sounds = dict(config.items('DEFAULT'))
        for key, path in self.sounds.items():
            self.sounds[key] = pygame.mixer.Sound(path)


    def init_screen_matrix(self):
        self.screen = np.empty((self.HEIGHT-1, self.WIDTH-1, 5), dtype='U3')
        self.screen[True] = self.empty_space_chr

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
            elif key == key.backspace:
                if self.screen[self.Y, self.X, 0] == self.empty_space_chr:
                    self.Y, self.X, _ = self.move_coord(self.Y, self.X, (0, -1))
                self.screen[self.Y, self.X, :] = self.empty_space_chr
        elif type(key) == keyboard.KeyCode:
            if key.char == self.set_runner:
                self.screen[self.Y, self.X, 1] = self.runner_chr
                self.screen[self.Y, self.X, 3] = '-1'
                self.screen[self.Y, self.X, 4] = '-1'
            elif key.char == self.set_note:
                self.screen[self.Y, self.X, 0] = self.note_chr
            elif key.char == self.loop_begin:
                self.screen[self.Y, self.X, 0] = self.loop_begin_chr
                self.screen[self.Y, self.X, 2] = str(sum(self.screen[self.Y, :, 0] == self.loop_begin_chr) - 1)
            elif key.char == self.loop_end:
                self.screen[self.Y, self.X, 0] = self.loop_end_chr
                self.screen[self.Y, self.X, 2] = str(sum(self.screen[self.Y, :, 0] == self.loop_end_chr) - 1)
            elif key.char in self.sounds.keys():
                self.screen[self.Y, self.X, 0] = self.note_chr
                self.screen[self.Y, self.X, 2] = key.char
            else:
                self.screen[self.Y, self.X, 0] = key.char
                self.Y, self.X, _ = self.move_coord(self.Y, self.X, (0, 1))
            
            joined_row = ''.join(self.screen[self.Y, :, 0]) 
            if 'bpm' in joined_row:
                i = joined_row.index('bpm')
                for j in range(i-1, -1, -1):
                    if not joined_row[j].isnumeric():
                        j += 1
                        break
                if i-j > 1:
                    #print(joitype(i),type(j))
                    if int(joined_row[j:i]) in self.bpms.keys():
                        self.bpms[int(joined_row[j:i])][0].add(self.Y)
                    else:
                        self.bpms[int(joined_row[j:i])] = [{self.Y}, time.time()]
                    # remove row from global bpm
                    if self.Y in self.bpms[self.BPM][0]:
                        self.bpms[self.BPM][0].remove(self.Y)
        
    def on_release(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def draw_screen(self):
        self.console.erase()
        for y in range(self.screen.shape[0]):
            for x in range(self.screen.shape[1]):
                # highlight and play when selector position
                color = curses.A_STANDOUT if y==self.Y and x==self.X else curses.COLOR_BLACK
                if self.screen[y, x, 1] == self.empty_space_chr:
                    character = self.screen[y, x, 0]
                else:
                    # highlight note when runner is on it
                    if self.screen[y, x, 0] == self.note_chr and self.screen[y, x, 1] == self.runner_chr: 
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

    def _get_start_pos(self, y, x, last_begin_loop):
        begin_loop_pos = np.argwhere(self.screen[y, :, 0] == self.loop_begin_chr)
        begin_loop_pos = [e for e in begin_loop_pos if e < x]
        if not len(begin_loop_pos):
            # there is no begin loop set, go back to line beginning instead
            return 0, -1
        last_begin_loop += 1
        if last_begin_loop >= len(begin_loop_pos):
            last_begin_loop = 0
        return np.argwhere(self.screen[y, :, 2] == str(last_begin_loop))[0,0] + 1, last_begin_loop
    
    def move_runner(self, rows):
        for y, x, _ in [e for e in np.argwhere(self.screen==self.runner_chr)[::-1] if e[0] in list(rows)]:
            # get next position and if that next position is offscreen
            _, nx, movable = self.move_coord(y, x, (0, 1))
            self.screen[y, x, 1] = self.empty_space_chr
            last_endloop = int(self.screen[y, x, 3])
            last_beginloop = int(self.screen[y, x, 4])
            self.screen[y, x, 3] = self.empty_space_chr
            self.screen[y, x, 4] = self.empty_space_chr
            if movable:
                # check for loop
                end_loop_pos = np.argwhere(self.screen[y, :, 0] == self.loop_end_chr)
                if nx in end_loop_pos:
                    if nx == max(end_loop_pos):
                        last_endloop = self.screen[y, nx, 2]
                        nx, last_beginloop = self._get_start_pos(y, x, last_beginloop)
                    elif int(self.screen[y, nx, 2]) == last_endloop + 1:
                        last_endloop = self.screen[y, nx, 2]
                        nx, last_beginloop = self._get_start_pos(y, x, last_beginloop)
                    elif last_endloop + 1 >= len(end_loop_pos) and self.screen[y, nx, 2] == '0':
                        last_endloop = self.screen[y, nx, 2]
                        nx, last_beginloop = self._get_start_pos(y, x, last_beginloop)
                self.screen[y, nx, 1] = self.runner_chr
                self.screen[y, nx, 3] = str(last_endloop)
                self.screen[y, nx, 4] = str(last_beginloop)
            # check if note is hit and play
            if self.screen[y, nx, 0] == self.note_chr:
                pygame.mixer.Channel(self.current_channel).play(self.sounds[self.screen[y, nx, 2]])
                self.current_channel += 1
                if self.current_channel >= self.channel_number - 1:
                    self.current_channel = 0
                #pygame.mixer.Sound.play(self.sound)


    def draw(self):
        self.draw_screen()
        print(0)
        #self.bpms[self.BPM][1] = time.time()
        i=0
        while True:
            #self.update_size()
            i+=1
            nt = time.time()
            for bpm, (rows, t) in dict(self.bpms).items():
                if nt - t >= 60/bpm:
                    # visualize tempo
                    self.screen[list(rows), -1, 0] = 'O' if self.screen[list(rows)[0], -1, 0] != 'O' else 'o'
                    # move the runner
                    self.move_runner(rows)
                    self.bpms[bpm][1] = nt
            
            # draw screen after number of iterations (replace by frames/seconds)
            if i==250_000:
                self.update_size()
                self.draw_screen()
                i=0


if __name__ == "__main__":
    grid = Grid(240)
    grid.draw()