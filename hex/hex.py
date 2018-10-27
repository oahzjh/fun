"""
This is a python implementaiton of hex editor.
"""
import argparse
import curses
import binascii
import string
import enum
import os
import sys


class LessFile(object):
    def up(self):
        raise NotImplementedError()

    def down(self):
        raise NotImplementedError()

    def up_page(self):
        raise NotImplementedError()

    def down_page(self):
        raise NotImplementedError()

    def search(self, str):
        raise NotImplementedError()


class Less(object):
    """An module to interactive experience similar to unix less cmd"""

    def __init__(self, less_file):
        self.term_row = None
        self.term_col = None
        self._less_file = less_file

    def loop(self, stdsrc):

        try:
            self._loop(stdsrc)
        except KeyboardInterrupt:
            pass

    def _loop(self, stdsrc):
        self.term_row = curses.LINES - 1
        self.term_col = curses.COLS - 1

        # Fill the screen up to height of row
        for row in range(self.term_row):
            stdsrc.addstr(row, 0, self._less_file.down())

        while True:
            stdsrc.addstr(self.term_row, 0, ":")
            stdsrc.refresh()
            key = stdsrc.getch()
            if chr(key) in string.printable and chr(
                    key) not in string.whitespace:
                stdsrc.addstr(self.term_row, 1, "{} {}".format(chr(key), key))
            else:
                stdsrc.addstr(self.term_row, 1, "{}".format(key))

            # Handle navigation
            if key == curses.KEY_DOWN:
                stdsrc.addstr(self.term_row - 1, 0, self._less_file.down())
            elif key == curses.KEY_UP:
                stdsrc.addstr(self.term_row - 1, 0, self._less_file.up())
            elif key == 4:
                break


class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class Hex(LessFile):

    LINE_WORD_LENGTH = 4 * 4

    def __init__(self, input_file):
        self.input_file = input_file
        self.data = open(self.input_file, mode='rb').read()
        self.line_addr = 0
        self.direction = Direction.DOWN

    def pretty_hex_line(self, data_line, width=2):
        if len(data_line) % width:
            raise ValueError(
                "Invalid width {}! Width needs to be divisable by LINE_WORD_LENGTH({})"
                .format(width, len(data_line)))

        line_format_str = ("{:02x}" * width + " ") * int(
            len(data_line) / width)
        return line_format_str.format(*data_line)

    def pretty_ascii_line(self, data_line):
        line_str = ""
        for x in data_line:
            if not chr(x) in string.whitespace and chr(x) in string.printable:
                line_str += chr(x)
            else:
                line_str += '.'
        return line_str

    def pretty_line(self, data_line):
        return "{} {}".format(
            self.pretty_hex_line(data_line), self.pretty_ascii_line(data_line))

    def down(self):
        if self.direction != Direction.DOWN:
            self.line_addr += self.LINE_WORD_LENGTH

        line = "{:08x}: {}".format(
            self.line_addr,
            self.pretty_line(self.data[self.line_addr:self.line_addr +
                                       self.LINE_WORD_LENGTH]))
        self.line_addr += self.LINE_WORD_LENGTH
        self.direction = Direction.DOWN
        return line

    def up(self):
        if self.direction != Direction.UP:
            self.line_addr -= self.LINE_WORD_LENGTH

        self.line_addr -= self.LINE_WORD_LENGTH
        self.direction = Direction.UP

        line = "{:08x}: {}".format(
            self.line_addr,
            self.pretty_line(self.data[self.line_addr:self.line_addr +
                                       self.LINE_WORD_LENGTH]))
        return line


def get_argparser():
    parser = argparse.ArgumentParser(description="Argument parser hex")
    parser.add_argument("-i", "--input", required=True, type=str)
    return parser


def main():
    parse_arg = get_argparser().parse_args()

    hex = Hex(parse_arg.input)

    row, col = os.popen('stty size', 'r').read().split()
    less = Less(hex)
    curses.wrapper(less.loop)


if __name__ == "__main__":
    main()
