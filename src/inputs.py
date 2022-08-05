from pynput import keyboard
import curses


class Inputs:
    """This manages keyboard and mouse inputs.
    
    :param config: all paramaters needed to manage inputs
    :type config: dictonary
    :param grid_manager: a grid manager object
    :type grid_manager: src.grid.Grid
    """

    def __init__(self, config, grid_manager):
        """Constructor function"""
        self.loop_begin = config['loop_begin']
        self.loop_end = config['loop_end']

        self.grid = grid_manager

        # init keyboard listener
        keyboard_listener = keyboard.Listener(on_press=self.on_press,
                                              on_release=self.on_release)
        keyboard_listener.start()

        # mouse intialization
        curses.curs_set(0) 
        self.grid.console.keypad(1) 
        self.grid.console.nodelay(1)
        curses.mousemask(1)
        # true if escape was pressed once, else false
        self.esc_pressed = False


    def on_press(self, key):
        """"Manage key press.
        
        :param key: pressed key
        :type key: either keyboard.Key or keyboard.KeyCode for special keys
        """
        if type(key) == keyboard.Key:  # special keys
            if key == key.down:
                # move cursor down
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (1, 0))
            elif key == key.up:
                # move cursor up
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (-1, 0))
            elif key == key.left:
                # move cursor left
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (0, -1))
            elif key == key.right:
                # move cursor right
                self.grid.Y, self.grid.X, _ = self.grid.move_coord(self.grid.Y,
                                                                   self.grid.X,
                                                                   (0, 1))
            elif key == key.backspace:
                # delete the element the cursor is on
                self.grid.delete_element()
            elif key == key.enter:
                # place a runner at position cursor is on
                self.grid.set_runner()
            elif key == key.shift_l:
                # place selected sound-key
                self.grid.place_note(self.grid.selected_key)
            elif key == key.shift_r:
                # save grid
                self.grid.save_grid()
            elif key == key.esc:
                # stop application
                self.esc_pressed = True
        elif type(key) == keyboard.KeyCode:  # alphanumeric keys
            if key.char == self.loop_begin:
                # set a begin loop
                self.grid.grid[self.grid.Y, self.grid.X, 0] = self.grid.loop_begin_chr
                # set order-number
                on = str(sum(self.grid.grid[self.grid.Y, :, 0] == self.grid.loop_begin_chr) - 1)
                self.grid.grid[self.grid.Y, self.grid.X, 2] = on
            elif key.char == self.loop_end:
                # set an end loop
                self.grid.grid[self.grid.Y, self.grid.X, 0] = self.grid.loop_end_chr
                # set order number
                on = str(sum(self.grid.grid[self.grid.Y, :, 0] == self.grid.loop_end_chr) - 1)
                self.grid.grid[self.grid.Y, self.grid.X, 2] = on
            elif key.char in self.grid.sound_manager.sounds.keys():
                # place sound-key
                self.grid.place_note(key.char)
            elif key.char.isnumeric():
                # change a number
                self.grid.change_number(key.char)


    def on_release(self, key):
        """Manage key on release event.
        
        :param key: released key
        :type key: either keyboard.Key or keyboard.KeyCode for special keys
        """
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        
        
    def mouse_check(self):
        """Check for a mouse check and react accordingly."""
        event = self.grid.console.getch()
        #if event == ord("q"):
        #    return
        if event == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            self.grid.Y = my
            self.grid.X = mx
            # check if mouse clicked the right side menu
            if mx > self.grid.grid.shape[1] + self.grid.end_grid_index + 1:
                if my == self.grid.grid.shape[0] - 1:
                    # last row was pressed, move first sound index down
                    self.grid.first_sound_index += 6
                elif my == 0:
                    # first row was pressed, move first row up
                    self.grid.first_sound_index -= 6
                self.grid.write_sound_menu(selected_row=my)
