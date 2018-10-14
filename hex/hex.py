"""
This is a python implementaiton of hex editor.
"""
import argparse
import binascii
import string
import os
import sys


class Hex(object):

    LINE_WORD_LENGTH = 4 * 4

    def __init__(row, col, input_file):
        self.term_row = row
        self.term_col = col
        self.input_file = input_file

    def pretty_hex_line(data_line, width=2):
        if len(data_line) % width:
            raise ValueError(
                "Invalid width {}! Width needs to be divisable by LINE_WORD_LENGTH({})"
                .format(width, len(data_line)))

        line_format_str = ("{:02x}" * width + " ") * int(
            len(data_line) / width)
        return line_format_str.format(*data_line)

    def pretty_ascii_line(data_line):
        line_str = ""
        for x in data_line:
            if not chr(x) in string.whitespace and chr(x) in string.printable:
                line_str += chr(x)
            else:
                line_str += '.'
        return line_str

    def pretty_line(data_line):
        return "{} {}".format(
            pretty_hex_line(data_line), pretty_ascii_line(data_line))

    def print_pretty(data):
        line_addr = 0
        while data:
            print("{:08x}: {}".format(line_addr,
                                      pretty_line(data[:LINE_WORD_LENGTH])))
            line_addr += LINE_WORD_LENGTH
            data = data[LINE_WORD_LENGTH:]


def get_argparser():
    parser = argparse.ArgumentParser(description="Argument parser hex")
    parser.add_argument("-i", "--input", required=True)
    return parser


def main():
    parse_arg = get_argparser().parse_args()

    row, col = os.popen('stty size', 'r').read().split()

    hex = Hex(row, col, parse_arg.input_file)
    hex.print_pretty()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
