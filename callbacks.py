import curses
from curses import wrapper
import sys

class IOCallbacks(object):
    pass

class DefualtCallbacks(IOCallbacks):
    @staticmethod
    def on_output(value, is_number=False):
        ending = '\n' if is_number else ''
        print(value, end=ending)

    @staticmethod
    def get_input():
        return input('?: ')

    @classmethod
    def get_keypress(cls, win=None):
        if win is None:
            return wrapper(cls.get_keypress)

        try:
            return int.from_bytes(win.getkey(), byteorder=sys.byteorder)
        except Exception as e:
            return 0
