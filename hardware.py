#coding=utf-8
from constants import *

class Display(object):
    """docstring for Display."""
    def __init__(self, serialport, w=W, h=H):
        super(Display, self).__init__()
        self.serialport = serialport
        self.grid_h = h
        self.grid_w = w
        return

    def get_cmds(self):
        """Check serial in port for messages. If commands come in, delegate calls to relevant components"""
        return {'cmd': None}
        return {'cmd': 'note', 'x': grid_x, 'y': self.grid_h - grid_y -1}
        return {'cmd': 'ins', 'ins': ins}
        return {'cmd': 'add_page'}
        return {'cmd': 'change_division', 'div': (-1 if (x-self.page_x <=5) else 1)}
        return {'cmd': 'dec_rep', 'page': y-self.page_y-1}
        return {'cmd': 'page_down', 'page': y-self.page_y-1}
        return {'cmd': 'page_up', 'page': y-self.page_y-1}
        return {'cmd': 'inc_rep', 'page': y-self.page_y-1}

    def draw_all(self, status, led_grid):
        """Send commands to serial out which describe display status:
        Typically, LED grid data, plus auxillary status of instruments, pages etc.
        Each RGB pixel's data is 24bit number.
        24bits*256pixels/1Byte = 768Bytes. Max Bitrate = 14400B/s. Refresh rate, latency = 1/18s.
        18fps is good, but is 1/18s latency acceptable?
        We know most of the display state ahead of time, is it possible to compensate for latency?
        If full LED grid is too much data, only send diffs, but do full refresh every x frames"""
        buffer = []
        for c, column in enumerate(led_grid):  # row counter
            for r, cell in enumerate(column):  # column counter
                R,G,B = LED_DISPLAY[cell]
                buffer.append(R,G,B)
        status_stream = convert_somehow(status)
        stream.append(status_stream)
        stream = ''.join(buffer)
        serial.write(stream)
        return