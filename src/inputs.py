from pynput import keyboard
import curses


class Inputs:

    def __init__(self, config, grid_manager):
        self.loop_begin = config['loop_begin']
        self.loop_end = config['loop_end']

        self.grid = grid_manager

        # init keyboard listener
        keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        keyboard_listener.start()
        self.pressed_cmd = False

        # mouse intialization
        curses.curs_set(0) 
        self.grid.console.keypad(1) 
        self.grid.console.nodelay(1)
        curses.mousemask(1)


    def on_press(self, key):
        if type(key) == keyboard.Key:
            if key == key.down:
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (1, 0))
            elif key == key.up:
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (-1, 0))
            elif key == key.left:
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (0, -1))
            elif key == key.right:
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (0, 1))
            elif key == key.backspace:
                self.grid.grid[self.grid.Y, self.grid.X, :] = self.grid.empty_space_chr
                self.grid.change_number('0')
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (0, -1))
            elif key == key.enter:
                self.grid.set_runner()
            self.pressed_cmd = key == key.cmd
        elif type(key) == keyboard.KeyCode:
            if key.char == self.loop_begin:
                self.grid.grid[self.grid.Y, self.grid.X, 0] = self.grid.loop_begin_chr
                self.grid.grid[self.grid.Y, self.grid.X, 2] = str(sum(self.grid.grid[self.grid.Y, :, 0] == self.grid.loop_begin_chr) - 1)
            elif key.char == self.loop_end:
                self.grid.grid[self.grid.Y, self.grid.X, 0] = self.grid.loop_end_chr
                self.grid.grid[self.grid.Y, self.grid.X, 2] = str(sum(self.grid.grid[self.grid.Y, :, 0] == self.grid.loop_end_chr) - 1)
            elif key.char in self.grid.sound_manager.sounds.keys():
                self.grid.place_note(key.char)
            elif self.pressed_cmd and key.char == 'v':
                self.grid.place_note(self.grid.selected_key)
            elif key.char.isnumeric():
                self.grid.change_number(key.char)


    def on_release(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        
        
    def mouse_check(self):
        event = self.grid.console.getch()
        if event == ord("q"):
            return 
        if event == curses.KEY_MOUSE:
            _, mx, my, _, state = curses.getmouse()
            self.grid.Y = my
            self.grid.X = mx
            # check where mouse was clicked and take action accordingly
            if mx > self.grid.grid.shape[1] + self.grid.end_grid_index + 1:
                if my == self.grid.grid.shape[0] - 1:
                    self.grid.current_sound_index += 6
                    self.grid.write_sound_menu()
                elif my == 0:
                    self.grid.current_sound_index -= 6
                    self.grid.write_sound_menu()
                else:
                    self.grid.write_sound_menu(selected_row=my)
