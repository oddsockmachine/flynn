# coding=utf-8
from instruments.instrument import Instrument
import constants as c
import note_conversion as n
import mido
from collections import namedtuple

Key = namedtuple('Key', 'letter number sprite')


class Keyboard(Instrument):
    """Keyboard
    - Choose between 3 types of keyboard
    - Piano: white and black keys along 2x rows, octaves up y. Highlight scale keys?
    -  x x  x x x_____
    - o x xx x x xo___
    - Scalar: Only show keys in scale, highlight root, octaves along y
    - oxxxxxxoxxxxxx__
    - Isomorphic: isomorphic/hex grid
    - Fretboard/linnstrument, hightlight scale + root keys
    """

    def __init__(self, ins_num, mport, key, scale, octave=1, speed=1):
        super(Keyboard, self).__init__(ins_num, mport, key, scale, octave, speed)
        if not isinstance(ins_num, int):
            print("Instrument num {} must be an int".format(ins_num))
            exit()
        self.type = "Keyboard"
        self.height = 16
        self.width = 16
        self.layout = "guitar"
        self.available_layouts = ['piano', 'scalar', 'isomorphic', 'guitar']
        self.cached_keys = (None, [])
        self.set_layout(self.layout)

    def set_key(self, key):
        c.logging.info("new key, regen layout")
        self.key = key
        self.set_layout(self.layout)
        return

    def set_scale(self, scale):
        c.logging.info("new key, regen layout")
        self.scale = scale
        self.set_layout(self.layout)
        return

    def set_layout(self, layout):
        if layout not in self.available_layouts:
            return
        self.layout = layout
        # self.cached_keys = (layout, self.keys_to_led_grid(create_piano_grid(self.scale, self.key)))
        if layout == 'piano':
            self.cached_keys = ('piano', rotate_grid(create_piano_grid(self.scale, self.key)))
        if layout == 'guitar':
            self.cached_keys = ('guitar', rotate_grid(create_guitar_grid(self.scale, self.key)))
        if layout == 'scalar':
            self.cached_keys = ('scalar', rotate_grid(create_scalar_grid(self.scale, self.key)))

        return

    def get_status(self):
        status = {
            'ins_num': self.ins_num+1,
            'ins_total': 16,
            'page_num': 0,
            'page_total': 0,
            'repeat_num': 0,
            'repeat_total': 0,
            'page_stats': {},
            'key': str(self.key),
            'scale': str(self.scale),
            'octave': str(self.octave),
            'type': self.type,
            'division': self.get_beat_division_str(),
            'random_rpt': False,
            'sustain': False,
        }
        return status

    def touch_note(self, state, x, y):
        '''touch the x/y cell on the current page'''
        if y < 14:
            key = self.cached_keys[1][x][y]
            c.logging.info(key.number)
            # add to new_notes
        return True

    def keys_to_led_grid(self, keys):
        # c.logging.info(len(keys))
        # c.logging.info(keys[5][5])
        grid = [[None for x in range(c.W)] for y in range(c.H)]
        for y, row in enumerate(keys):
            for x, key in enumerate(row):
                grid[y][x] = key.sprite
        # TODO add buttons over top
        return grid

    def get_led_grid(self, state):
        # if self.layout == self.cached_keys[0]:
        return self.keys_to_led_grid(self.cached_keys[1])
        # if self.layout == 'piano':
        #     self.cached_keys = ('piano', self.keys_to_led_grid(create_piano_grid(self.scale, self.key)))
        # if self.layout == 'guitar':
        #     self.cached_keys = ('guitar', self.keys_to_led_grid(create_guitar_grid(self.scale, self.key)))
        # if self.layout == 'scalar':
        #     self.cached_keys = ('scalar', self.keys_to_led_grid(create_scalar_grid(self.scale, self.key)))
        # return self.cached_keys[1]

    def step_beat(self, global_beat):
        '''Increment the beat counter, and do the math on pages and repeats'''
        local = self.calc_local_beat(global_beat)
        local
        new_notes = []
        # new_notes = self.get_curr_notes()
        self.output(self.old_notes, new_notes)
        self.old_notes = new_notes  # Keep track of which notes need stopping next beat
        return

    def output(self, old_notes, new_notes):
        """Return all note-ons from the current beat, and all note-offs from the last"""
        notes_off = [self.cell_to_midi(c) for c in old_notes]
        notes_on = [self.cell_to_midi(c) for c in new_notes]
        notes_off = [n for n in notes_off if n < 128 and n > 0]
        notes_on = [n for n in notes_on if n < 128 and n > 0]
        off_msgs = [mido.Message('note_off', note=n, channel=self.ins_num) for n in notes_off]
        on_msgs = [mido.Message('note_on', note=n, channel=self.ins_num) for n in notes_on]
        msgs = off_msgs + on_msgs
        if self.mport:  # Allows us to not send messages if testing. TODO This could be mocked later
            for msg in msgs:
                self.mport.send(msg)

    def save(self):
        saved = {
          "droplet_velocities": self.droplet_velocities,
          "droplet_positions": self.droplet_positions,
          "droplet_starts": self.droplet_starts,
        }
        saved.update(self.default_save_info())
        return saved

    def load(self, saved):
        self.load_default_info(saved)
        self.droplet_velocities = saved["droplet_velocities"]
        self.droplet_positions = saved["droplet_positions"]
        self.droplet_starts = saved["droplet_starts"]
        return

    def clear_page(self):
        self.get_curr_page().clear_page()
        return


class Key(object):
    """docstring for Key."""

    def __init__(self, number, sprite):
        super(Key, self).__init__()
        self.letter = n.midi_to_letter(number)
        self.number = number
        self.sprite = sprite

    def __repr__(self):
        # return str(self.letter)
        return c.DISPLAY[self.sprite]


def get_keys_for_scale(row_scale, starting_note, rotate, length, scale, key, b_w):
    keys = []
    scale_notes = n.create_cell_to_midi_note_lookup(scale, -1, key, 62).values()
    scale = n.SCALE_INTERVALS[row_scale]
    for interval in scale:
        keys.append(1)
        for gap in range(interval-1):
            keys.append(0)
    if rotate:
        keys = keys[rotate:] + keys[:rotate]
    while (len(keys) < length):
        keys.extend(keys)
    for i, k in enumerate(keys):
        if k == 1:
            keys[i] = i + starting_note+1
    for i, k in enumerate(keys):
        if k in scale_notes:
            keys[i] = Key(k, c.KEY_SCALE)
        elif k == 0:
            keys[i] = Key(0, c.LED_BLANK)
        else:
            keys[i] = Key(k, c.KEY_WHITE if b_w == 'w' else c.KEY_BLACK)
    return keys[:length]


def create_piano_grid(scale, key):
    grid = []
    grid.append([Key(0, c.LED_BLANK) for x in range(c.W)])
    grid.append([Key(0, c.LED_BLANK) for x in range(c.W)])
    offset = 23
    print(c.H-1/2)
    for h in range(int((c.H-1)/2))[::-1]:
        print(h)
        w_keys = get_keys_for_scale('major', (h * 12) + offset, 0, c.W, scale, key, 'w')
        b_keys = get_keys_for_scale('pentatonic_maj', (h * 12) + offset, 6, c.W, scale, key, 'b')
        # grid.append([Key(0, c.LED_BLANK) for x in range(c.W)])
        grid.append(b_keys)
        grid.append(w_keys)
    print(len(grid))
    while (len(grid) < c.W):  # TODO put blank lines at top
        grid.extend([[Key(0, c.LED_BLANK) for x in range(c.W)]])
    print(len(grid))
    return grid



def create_scalar_grid(scale, key):
    keys = []
    for octave, y in enumerate(range(7)):
        keys.append(list(n.create_cell_to_midi_note_lookup(scale, octave, key, c.W).values()))
    grid = []
    for x in range(5):
        grid.append([Key(0, c.LED_BLANK) for i in range(c.W)])
    for row in keys[::-1]:
        grid.append([Key(k, c.KEY_ROOT if (i % 7) else c.KEY_SCALE) for i, k in enumerate(row)])
        # grid.append([Key(0, c.LED_BLANK) for i in row])
        # grid.append([Key(0, c.LED_BLANK) for i in row])
    for x in range(4):
        grid.append([Key(0, c.LED_BLANK) for i in range(c.W)])
    return grid



def create_guitar_grid(scale, key):
    scale_notes = n.create_cell_to_midi_note_lookup(scale, -1, key, 62).values()
    root_notes = list(scale_notes)[::(5 if 'penta' in scale else 7)]
    print(root_notes)
    print(scale_notes)
    print(n.midi_to_letter(list(scale_notes)[0]))
    start = 21 + n.KEYS.index(key)
    print(start)
    grid = []
    for i, r in enumerate(range(c.H-2)):
        row = []
        for x in range(c.W):
            note = start + x
            sprite = c.KEY_SCALE if note in scale_notes else c.KEY_WHITE
            if note in root_notes:
                sprite = c.KEY_ROOT
            row.append(Key(note, sprite))
        start += 5
        grid.append(row)
    grid.append([Key(0, c.LED_BLANK) for i in range(c.W)])
    grid.append([Key(0, c.LED_BLANK) for i in range(c.W)])
    return grid[::-1]


def rotate_grid(keys):
    grid = [[None for x in range(c.W)] for y in range(c.H)]
    for y, row in enumerate(keys):
        for x, key in enumerate(row):
            grid[x][c.H-y-1] = key
    return grid
