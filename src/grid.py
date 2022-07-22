from ast import JoinedStr
from ntpath import join
from numbers import Number
import numpy as np
import curses


class Grid:
    
    def __init__(self, config, sound_manager):
        self.ticks = config['ticks']
        self.global_bpm = config['global_bpm']
        self.empty_space_chr = config['empty_space_chr']
        self.runner_chr = config['runner_chr']
        self.loop_begin_chr = config['loop_begin_chr']
        self.loop_end_chr = config['loop_end_chr']
        self.sound_manager = sound_manager

        self.begin_grid_index = 9

        # init console
        self.console = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, 235)
        curses.init_pair(5, curses.COLOR_GREEN, 235)
        curses.init_pair(6, -1, curses.COLOR_WHITE)
        #for i in range(0, curses.COLORS):
        #    curses.init_pair(i + 1, i, -1)
        self.HEIGHT, self.WIDTH = self.console.getmaxyx()
        self.Y, self.X = 0, 0  # y and x position of the selector

        # initalize screen
        self.init_grid()

        # save bpms as keys and as items the corresponding rows, time
        self.bpms = {self.global_bpm: [list(range(self.grid.shape[0]))[::2], 0]}
        for bpm, (rows, _) in self.bpms.items():
            bpm_text = list(str(bpm) + 'bpm')
            self.grid[rows, :len(bpm_text), 0] = bpm_text

        # volumes for each row
        self.volumes = {row: 1 for row in range(self.grid.shape[0])[::2]}
        for row, vol in self.volumes.items():
            vol_text = list(str(round(vol * 100)) + '% vol')
            self.grid[row+1, :len(vol_text), 0] = vol_text
        

    
    
    def init_grid(self):
        self.grid = np.empty((self.HEIGHT-1, self.WIDTH-1, 5), dtype='U3')
        self.grid[True] = self.empty_space_chr
        self.grid[:, :self.begin_grid_index - 1, 0] = ' '
        self.grid[1::2, :, 0] = ' '
        self.grid[::2, self.begin_grid_index - 1, 0] = '#'
        self.grid[1::2, self.begin_grid_index - 1, 0] = '#'
    

    def set_runner(self):
        # check if we are in the right row
        if not self.Y % 2:
            x = max(self.begin_grid_index, self.X)
            self.grid[self.Y, x, 1] = self.runner_chr
            self.grid[self.Y, x, 3] = '-1'
            self.grid[self.Y, x, 4] = '-1'
    
    
    def change_number(self, number: str):
        """Takes number and changes it in the grid at location self.Y and self.X.
        The function also tries to update the corresponding variable, f.e. self.bpms"""
        if not self.Y % 2:
            # change bpm
            bpm_position = ''.join(self.grid[self.Y, :, 0]).find('bpm')
            if bpm_position >= 0 and self.X < bpm_position:
                self.grid[self.Y, self.X, 0] = number
                new_bpm = int(''.join(self.grid[self.Y, :, 0])[:bpm_position])
                for bpm, (rows, _) in self.bpms.items():
                    if self.Y in rows:
                        rows.remove(self.Y)
                        self.bpms[bpm][0] = rows
                if new_bpm in self.bpms.keys():# and self.Y not in self.bpms[new_bpm][0]:
                    self.bpms[new_bpm][0].append(self.Y)
                else:
                    self.bpms[new_bpm] = [[self.Y], 0]
        else:
            # change volume
            vol_position = ''.join(self.grid[self.Y, :, 0]).find('% vol')
            if vol_position >= 0 and self.X < vol_position:
                new_vol = int(''.join(self.grid[self.Y, :, 0])[:vol_position])
                if new_vol > 100:
                    new_vol = 100
                self.grid[self.Y, :vol_position, 0] = list(str(new_vol))
                self.volumes[self.Y - 1] = new_vol/100


    
    def move_coord(self, y: int, x: int, dir: tuple) -> tuple:
        ny, nx = y + dir[0], x + dir[1]
        if nx == self.begin_grid_index - 1:
            nx += dir[1]
        if 0 <= nx < self.grid.shape[1] and 0 <= ny < self.grid.shape[0]:
            return ny, nx, True
        return y, x, False


    def _get_start_pos(self, y, x, last_begin_loop) -> tuple:
        begin_loop_pos = np.argwhere(self.grid[y, :, 0] == self.loop_begin_chr)
        begin_loop_pos = [e for e in begin_loop_pos if e < x]
        if not len(begin_loop_pos):
            # there is no begin loop set, go back to line beginning instead
            return self.begin_grid_index, -1
        last_begin_loop += 1
        if last_begin_loop >= len(begin_loop_pos):
            last_begin_loop = 0
        return np.argwhere(self.grid[y, :, 2] == str(last_begin_loop))[0,0] + 1, last_begin_loop
    

    def move_runners(self, time):
        for bpm, (rows, t) in dict(self.bpms).items():
            if bpm > 0 and time - t >= 60/bpm:
                self.bpms[bpm][1] = time
                # iterate through all rows with bpm
                for row in rows:
                    # visualize beat
                    self.grid[row, self.begin_grid_index - 2, 0] = '÷' if self.grid[row, self.begin_grid_index - 2, 0] == '-' else '-'
                    # find every runner in a row
                    for x in np.argwhere(self.grid[row, :, 1] == self.runner_chr)[::-1]:
                        x = x[0]
                        # get next x position
                        # get next position and if that next position is offscreen
                        _, nx, movable = self.move_coord(row, x, (0, 1))
                        self.grid[row, x, 1] = self.empty_space_chr
                        last_endloop = int(self.grid[row, x, 3])
                        last_beginloop = int(self.grid[row, x, 4])
                        self.grid[row, x, 3] = self.empty_space_chr
                        self.grid[row, x, 4] = self.empty_space_chr
                        if movable:
                            # check for loop
                            end_loop_pos = np.argwhere(self.grid[row, :, 0] == self.loop_end_chr)
                            if nx in end_loop_pos:
                                if nx == max(end_loop_pos):
                                    last_endloop = self.grid[row, nx, 2]
                                    nx, last_beginloop = self._get_start_pos(row, x, last_beginloop)
                                elif int(self.grid[row, nx, 2]) == last_endloop + 1:
                                    last_endloop = self.grid[row, nx, 2]
                                    nx, last_beginloop = self._get_start_pos(row, x, last_beginloop)
                                elif last_endloop + 1 >= len(end_loop_pos) and self.grid[row, nx, 2] == '0':
                                    last_endloop = self.grid[row, nx, 2]
                                    nx, last_beginloop = self._get_start_pos(row, x, last_beginloop)
                            self.grid[row, nx, 1] = self.runner_chr
                            self.grid[row, nx, 3] = str(last_endloop)
                            self.grid[row, nx, 4] = str(last_beginloop)
                            # check if note is hit and play it
                            if self.grid[row, nx, 0] in self.sound_manager.sounds.keys():
                                self.sound_manager.play(self.grid[row, nx, 0], self.volumes[row])

    
    def draw_grid(self):
        self.console.erase()
        # iterate through grid
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                # check if we are not dealing with a runner
                if self.grid[y, x, 1] == self.empty_space_chr:
                    # use character from channel 0
                    character = self.grid[y, x, 0]
                    if character == '#':
                        # border color
                        color = curses.color_pair(1)
                    elif (y//2)%2:
                        if character==self.empty_space_chr and (x + self.begin_grid_index - 1) % self.ticks == 0:
                            color = curses.color_pair(3)
                        else:
                            color = curses.color_pair(2)
                    else:
                        if character==self.empty_space_chr and (x + self.begin_grid_index - 1) % self.ticks == 0:
                            color = curses.color_pair(5)
                        else:
                            color = curses.color_pair(4)
                else:
                    # highlight note when runner is on it
                    if self.grid[y, x, 0] in self.sound_manager.sounds.keys() and self.grid[y, x, 1] == self.runner_chr: 
                        character = self.grid[y, x, 0]
                        color = curses.color_pair(6)
                    else:
                        character = self.grid[y, x, 1]
                        color = curses.color_pair(2 if (y//2)%2 else 4)
                # highlight and play when selector position
                if y==self.Y and x==self.X:
                    color = curses.color_pair(6)
                self.console.addch(y, x, character, color)
        self.console.refresh()