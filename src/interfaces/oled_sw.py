from threading import Thread
from pykka import ThreadingActor
from constants import debug, TICK, BEAT
from time import sleep
from random import randint
from buses import OLED_bus
from interfaces.oled_abstract import OLED_abstract

# TODO create an ABC/interface for OLED, then implementations for hw and sw

class OLED_Screens(ThreadingActor, OLED_abstract):
    """4x OLED screens
    Send text/animations to each"""
    def __init__(self, num_screens):
        super().__init__()
        self.OLED_bus = OLED_bus
        self.i2c = None
        self.num_screens = num_screens
        self.screens = []
        for i in range(num_screens):
            oled = OLED.start(i).proxy()
            self.screens.append(oled)
        self.assignments = ["" for l in range(self.num_screens)]

    def text(self, screen_num, text):
        """Write text to the relevant line in a particular style (highlighted, plain, inverted, etc)"""
        if screen_num >= self.num_screens:
            return
        self.screens[screen_num].text(text)
        return

    def get_text(self):
        lines = [s.get_text().get() for s in self.screens]
        return lines

    def set_encoder_assignment(self, assignment, screen_num=None):
        if screen_num is None:
            for i in range(self.num_screens):
                if len(assignment[i]) > 0:
                    self.assignments[i] = assignment[i]
                    self.screens[i].set_encoder_assignment(assignment[i])
            return                
        if screen_num > self.num_screens:
            return
        self.assignments[screen_num] = assignment
        self.screens[screen_num].set_encoder_assignment(assignment)
        return

    def create_menu(self, screen_num, items):
        self.screens[screen_num].create_menu(items)
        # debug(self.screens[screen_num].text_lines)
        return

    def menu_scroll(self, screen_num, up_down):
        self.screens[screen_num].menu_scroll(up_down)
        return

    def get_menu_item(self, screen_num):
        return self.screens[screen_num].get_menu_item().get()

class OLED(ThreadingActor):
    def __init__(self, num):
        super().__init__()
        # Thread.__init__(self, name='OLED_'+str(num))
        self.num = num
        self.address = 0x00
        self.max_lines = 7
        self.max_chars = 20
        self.menu_mode = False
        self.menu_window_start = 0
        self.menu_window_height = self.max_lines - 1 
        self.highlight_line = 0
        self.text_lines = ["" for l in range(self.max_lines)]
    
    def text(self, text):
        """Write text to the relevant line in a particular style (highlighted, plain, inverted, etc)"""
        text = text[:self.max_lines-1]
        for i in range(self.max_lines-1):
            if i >= len(text):
                break
            self.text_lines[i] = text[i]
        return

    def highlight(self, line_no, style):
        return

    def clear(self):
        self.text_lines = ["" for l in range(self.max_lines)]
        return

    def get_text(self):
        return self.text_lines

    def set_encoder_assignment(self, assignment):
        self.text_lines[-1] = assignment
        return

    def gen_menu(self):
        debug(str(self.menu_window_start))
        debug(str(self.menu_window_height))
        debug(self.menu_items[self.menu_window_start:self.menu_window_start+self.menu_window_height]   )
        for i, item in enumerate(self.menu_items[self.menu_window_start:self.menu_window_height]):
            if i > len(self.menu_items):
                break
            if i == self.highlight_line:
                self.text_lines[i] = f">{item}"
            else:
                self.text_lines[i] = item

    
    def create_menu(self, items):
        self.menu_mode = True
        self.menu_items = items
        self.highlight_line = 0
        self.clear()
        self.menu_window_start = 0
        self.menu_window_height = self.max_lines - 1
        self.gen_menu()
        # for i, item in enumerate(self.menu_items[self.menu_window[0]:self.menu_window[1]]):
        #     debug("!")
        #     debug(i)
        #     if i > len(self.menu_items):
        #         break
        #     if i == self.highlight_line:
        #         self.text_lines[i] = f">{item}"
        #     else:
        #         debug(i)
        #         debug(item)
        #         self.text_lines[i] = item
        return

    def menu_scroll(self, up_down):
        if not self.menu_mode:
            return
        debug(f"scroll {up_down}")
        if up_down == "up" and self.highlight_line > 0:
            if self.highlight_line == self.menu_window_start:
                debug("<<")
                self.menu_window_start -= 1
            else:
                self.highlight_line -= 1
            # self.highlight_line -= 1
        elif up_down == "down" and self.highlight_line < len(self.menu_items):
            if self.highlight_line == self.menu_window_height:
                debug(">>")
                self.menu_window_start +=1 
            else:
                self.highlight_line += 1
            # self.highlight_line += 1
        debug(f"hi {self.highlight_line}")
        self.gen_menu()
        return

    def get_menu_item(self):
        num = self.highlight_line + self.menu_window_start
        return (num, self.menu_items[num])
