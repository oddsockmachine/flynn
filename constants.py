import logging
logging.basicConfig(filename='sequencer.log',level=logging.DEBUG)

LED_BLANK = 0
LED_SELECT = 1
LED_CURSOR = 2
LED_ACTIVE = 3

NOTE_OFF = 0
NOTE_ON = 3

DISPLAY = {0: '. ', 1:'░░', 2:'▒▒', 3:'▓▓'}

W = 16
H = 16

MAX_INSTRUMENTS = 16
