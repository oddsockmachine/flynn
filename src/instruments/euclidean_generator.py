# coding=utf-8
from instruments.sequencer import Sequencer
import constants as c
from note_grid import Note_Grid
from note_conversion import create_cell_to_midi_note_lookup
from screens import euc_cfg_grid_defn, generate_screen, get_cb_from_touch


class Euclidean(Sequencer):
    """Euclidean Beat Generator
    - For each drum-note/sample, set a bar length (<16), euclidean density, and offset
    - Bottom 16x8 shows 8 bar lengths, with hits highlighted. Beatpos moves across, or bar rotates?
    - Clicking on a bar determines its bar length
    - TopLeft 8x8 shows sliders for euclidean density. Clicking on a slider sets density
    - TopRight 8x8 shows sliders for offset. Is this necessary?"""

    def __init__(self, ins_num, mport, key, scale, octave=1, speed=1):
        super(Euclidean, self).__init__(ins_num, mport, key, scale, octave, speed)
        self.type = "Euclidean"
        self.densities = [0 for x in range(8)]
        self.offsets = [0 for x in range(8)]
        self.lengths = [16 for x in range(8)]
        self.curr_notes_pos = [0 for x in range(8)]
        self.fill = True
        self.scale = 'chromatic'
        self.octave = 1
        self.key = 'c'
        self.is_drum = (True, scale, key, octave)
        for i in range(8):
            self.regen(i)
        self.note_converter = create_cell_to_midi_note_lookup(self.scale, self.octave, self.key, self.height)

    def restart(self):
        """Set all aspects of instrument back to starting state"""
        self.curr_notes_pos = [0 for x in range(8)]
        return

    def euclidean_algo(self, pulses, rotate, steps):
        pattern = []
        bucket = 0
        for i in range(steps):
            bucket += pulses
            if bucket >= steps:
                bucket -= steps
                pattern.append(c.NOTE_ON)
            else:
                pattern.append(c.NOTE_OFF)
        rotate %= len(pattern)
        # rotate = 0 - rotate
        pattern = pattern[rotate:] + pattern[:rotate]
        pattern = pattern[::-1]
        for x in range(c.W - len(pattern)):
            pattern.append(c.NOTE_OFF)
        return pattern

    def regen(self, note):
        '''A parameter for this note has changed, regenerate sequence'''
        pulses, rotate, steps = self.densities[note], self.offsets[note], self.lengths[note]
        pattern = self.euclidean_algo(pulses, rotate, steps)
        page = self.get_curr_page()
        for i, beat in enumerate(page.note_grid):
            beat[note] = pattern[i]
        return

    def apply_control(self, x, y):
        if y >= 8:  # Control touch, but save it in the page, it's easier that way
            y -= 8
            if x < 8:  # densities
                self.densities[y] = 7 - x
            else:  # offsets
                self.offsets[y] = x - 8
        else:
            self.lengths[y] = x+1
        self.regen(y)
        return

    def touch_note(self, state, x, y):
        '''touch the x/y cell on the current page - either a control, or a note'''
        if state == 'play':
            # Is touch control or note?
            self.apply_control(x, y)
            # Apply touch to current temp page and source page
            # self.get_curr_page().touch_note(x, y)
        elif state == 'ins_cfg':
            cb_text, _x, _y = get_cb_from_touch(self.cb_grid, x, y)
            if not cb_text:
                return
            cb_func = self.__getattribute__('cb_' + cb_text)  # Lookup the relevant conductor function
            cb_func(_x, _y)  # call it, passing it x/y args (which may not be needed)
        return True

    # @pysnooper.snoop('./logz.log')
    def step_beat(self, global_beat):
        '''Increment the beat counter, and do the math on pages and repeats'''
        local = self.calc_local_beat(global_beat)
        if not self.has_beat_changed(local):
            # Intermediate beat for this instrument, do nothing
            return
        self.local_beat_position = local
        note_grid = self.get_curr_page().note_grid
        new_notes = []
        for i, n in enumerate(self.curr_notes_pos):
            n += 1
            limit = 16 if self.fill else self.lengths[i]
            if n >= limit:
                n = 0
            self.curr_notes_pos[i] = n
            if note_grid[n][i] == c.NOTE_ON:
                new_notes.append(i)
        self.output(self.old_notes, new_notes)
        self.old_notes = new_notes  # Keep track of which notes need stopping next beat
        return

    def get_led_status(self, cell, y, col_num):
        '''Determine which type of LED should be shown for a given cell'''
        led = c.LED_BLANK  # Start with blank / no led
        if y >= 8:
            return led
        if col_num == self.curr_notes_pos[y]:
            led = c.LED_BEAT  # If we're on the beat, we'll want to show the beat marker
            if cell == c.NOTE_ON:
                led = c.LED_SELECT  # Unless we want a selected + beat cell to be special
        elif cell == c.NOTE_ON:
            led = c.LED_ACTIVE  # Otherwise if the cell is active (touched)
        return led

    def get_led_grid(self, state):
        if state == 'play':
            led_grid = []
            grid = self.get_curr_page().note_grid
            for col_num, column in enumerate(grid):
                led_grid.append([self.get_led_status(x, y, col_num) for y, x in enumerate(column)])
            # Draw control sliders
            for y in range(8):
                # reset slider area (removes beat cursor)
                for x in range(16):
                    led_grid[x][y+8] = c.LED_BLANK
                for a in range(self.densities[y]+1):
                    led_grid[7-a][y+8] = c.LED_ACTIVE
                led_grid[7-self.densities[y]][y+8] = c.LED_SELECT
                led_grid[7][y+8] = c.LED_CURSOR
                for a in range(self.offsets[y]):
                    led_grid[8+a][y+8] = c.LED_ACTIVE
                led_grid[8+self.offsets[y]][y+8] = c.LED_SELECT
                led_grid[8][y+8] = c.LED_CURSOR
        elif state == 'ins_cfg':
            led_grid, cb_grid = generate_screen(euc_cfg_grid_defn, {
                'speed': int(self.speed),
                'octave': int(self.octave),
                'pages': [x.repeats for x in self.pages],
                'curr_p_r': (self.curr_page_num, self.curr_rept_num),
                'curr_page': self.curr_page_num,
                'next_page': self.get_next_page_num(),
                'fill': self.fill
                })
            self.cb_grid = cb_grid
            return led_grid
        return led_grid

    def save(self):
        saved = {
          "pages": [p.save() for p in self.pages],
          "sustain": self.sustain,
          "random_rpt": self.random_pages,
          "densities": self.densities,
          "offsets": self.offsets,
          "lengths": self.lengths,
          "curr_notes_pos": self.curr_notes_pos,
        }
        saved.update(self.default_save_info())
        return saved

    def load(self, saved):
        self.load_default_info(saved)
        self.sustain = saved["sustain"]
        self.random_pages = saved["random_rpt"]
        self.pages = []
        for p in saved["pages"]:
            page = Note_Grid(self.bars, self.height)
            page.load(p)
            self.pages.append(page)
        self.densities = saved["densities"]
        self.offsets = saved["offsets"]
        self.lengths = saved["lengths"]
        self.curr_notes_pos = saved["curr_notes_pos"]
        return
