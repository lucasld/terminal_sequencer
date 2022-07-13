# terminal_sequencer

### Goal Features:
- interaction through a terminal (in a 'grid')
- individual sequence parameters for each track
    - BPM
    - offset
    - sequence length - volume
    - instrument
- selector for different drum kits (sounds)
- grid is represented as np.ndarray (this enables saving of setup)
- option to export as .mp3/.wav

### Features:
- the grid is represented in a numpy array of shape WIDTH x HEIGHT x CHANNELS
    - WIDTH and HEIGHT is the size of the terminal -1
    - CHANNELS:
        - channel 0: encodes sequencer properties like note placement, loop placement
        - channel 1: exlusively encodes 'runner' positions. runners are the different 'note exiters' that move one step right each beat (better word for runner?)
        - channel 2: encodes additional information for elements from channel 0, as of yet only order of looper placement
        - channel 3: encodes number of last hit closing loop element
        - channel 4: encodes number of last hit opening loop element

