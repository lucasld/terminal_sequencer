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

        # init console
        self.console = curses.initscr()
        curses.start_color()
        self.HEIGHT, self.WIDTH = self.console.getmaxyx()
        self.Y, self.X = 0, 0  # y and x position of the selector


        # initalize screen
        self.init_grid()

        # save bpms as keys and as items the corresponding rows, time
        self.bpms = {self.global_bpm: [list(range(self.grid.shape[0])), 0]}
    
    
    def init_grid(self):
        self.grid = np.empty((self.HEIGHT-1, self.WIDTH-1, 5), dtype='U3')
        self.grid[True] = self.empty_space_chr

    
    def move_coord(self, y: int, x: int, dir: tuple) -> tuple:
        ny, nx = y + dir[0], x + dir[1]
        if 0 <= nx < self.grid.shape[1] and 0 <= ny < self.grid.shape[0]:
            return ny, nx, True
        return y, x, False


    def _get_start_pos(self, y, x, last_begin_loop):
        begin_loop_pos = np.argwhere(self.grid[y, :, 0] == self.loop_begin_chr)
        begin_loop_pos = [e for e in begin_loop_pos if e < x]
        if not len(begin_loop_pos):
            # there is no begin loop set, go back to line beginning instead
            return 0, -1
        last_begin_loop += 1
        if last_begin_loop >= len(begin_loop_pos):
            last_begin_loop = 0
        return np.argwhere(self.grid[y, :, 2] == str(last_begin_loop))[0,0] + 1, last_begin_loop
    

    def move_runners(self, time):
        for bpm, (rows, t) in dict(self.bpms).items():
            if time - t >= 60/bpm:
                self.bpms[bpm][1] = time
                # iterate through all rows with bpm
                for row in rows:
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
                                self.sound_manager.play(self.grid[row, nx, 0])
                                #pygame.mixer.Channel(self.current_channel).play(self.sounds[self.grid[row, nx, 2]])
                                #self.current_channel += 1
                                #if self.current_channel >= self.channel_number - 1:
                                #   self.current_channel = 0



    
    def draw_grid(self):
        self.console.erase()
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                # highlight and play when selector position
                color = curses.A_STANDOUT if y==self.Y and x==self.X else curses.COLOR_BLACK
                if self.grid[y, x, 1] == self.empty_space_chr:
                    character = self.grid[y, x, 0]
                else:
                    # highlight note when runner is on it
                    if self.grid[y, x, 0] in self.sound_manager.sounds.keys() and self.grid[y, x, 1] == self.runner_chr: 
                        character = self.grid[y, x, 0]
                        color = curses.A_STANDOUT
                    else:
                        character = self.grid[y, x, 1]
                self.console.addch(y, x, character, color)
        self.console.refresh()