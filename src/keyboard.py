from pynput import keyboard


class Keyboard:

    def __init__(self, config, grid_manager):
        self.loop_begin = config['loop_begin']
        self.loop_end = config['loop_end']

        self.grid = grid_manager

        # init listener
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()
    

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
        elif type(key) == keyboard.KeyCode:
            if key.char == self.loop_begin:
                self.grid.grid[self.grid.Y, self.grid.X, 0] = self.grid.loop_begin_chr
                self.grid.grid[self.grid.Y, self.grid.X, 2] = str(sum(self.grid.grid[self.grid.Y, :, 0] == self.grid.loop_begin_chr) - 1)
            elif key.char == self.loop_end:
                self.grid.grid[self.grid.Y, self.grid.X, 0] = self.grid.loop_end_chr
                self.grid.grid[self.grid.Y, self.grid.X, 2] = str(sum(self.grid.grid[self.grid.Y, :, 0] == self.grid.loop_end_chr) - 1)
            elif key.char in self.grid.sound_manager.sounds.keys():
                self.grid.grid[self.grid.Y, self.grid.X, 0] = key.char
            elif key.char.isnumeric():
                self.grid.change_number(key.char)
            
        
    def on_release(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False