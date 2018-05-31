import argparse
import curses
from time import time

import sys

import itertools


class State:
    def __init__(self, start, pause=None, scale=1):
        self.start = start
        self.pause = pause
        self.scale = scale

    def handle_key_press(self, k):
        if k == 'q':
            sys.exit(0)
        elif k == ' ':
            if self.pause:
                self.start += now() - self.pause
                self.pause = None
            else:
                self.pause = now()
        elif k == 'a':
            self.start += 5
        elif k == 'd':
            self.start -= 5
        elif k == 'z':
            self.scale += 0.1
        elif k == 'c':
            self.scale -= 0.1
        elif k == 'w':
            self.start += 500
        elif k == 'r':
            self.start -= 500


def get_time_from_str(t):
    t = t.split(':')
    return int((int(t[0])*3600 + int(t[1])*60 + float(t[2].replace(',', '.')))*10)


def now():
    return int(time() * 10)


def get_time_str(t):
    t = t // 10
    h = t // 3600
    t = t % 3600
    m = t // 60
    t = t % 60
    return ':'.join([str(i).zfill(2) for i in (h,m,t)])


def get_sub(line_no, lines):
    start = False
    sub_lines = []
    t0_ms = None
    t1_ms = None
    while line_no < len(lines) and (not start or lines[line_no]):
        if lines[line_no]:
            if not start:
                start = True
                line_no += 1
                t0, t1 = lines[line_no].split(' --> ')
                t0_ms = get_time_from_str(t0)
                t1_ms = get_time_from_str(t1)
            else:
                sub_lines.append(lines[line_no])
        line_no += 1

    sub_str = '\n'.join(sub_lines)
    sub = {}
    if t0_ms and t1_ms:
        sub = {t: sub_lines for t in range(t0_ms, t1_ms + 1)}
    return sub, line_no


def get_subtitles():
    parser = argparse.ArgumentParser(description='Display subtitles from file in a dark background')
    parser.add_argument('file', type=str, help='file path')

    options = parser.parse_args()

    try:
        with open(options.file, 'r') as f:
            lines = [l.strip('\n') for l in f.readlines()]
    except FileNotFoundError:
        print('File {} cannot be found'.format(options.file))
        sys.exit(1)

    subs = {}
    line_no = 0
    while line_no < len(lines):
        sub, line_no = get_sub(line_no, lines)
        subs.update(sub)

    return subs


def words_and_spaces(s):
    return list(itertools.chain.from_iterable(zip(s.split(), itertools.repeat(' '))))[:-1]


def print_centered(window, width, line, s):
    window.addstr(line, max(0, (width - len(s))//2), s, curses.A_BOLD)


def print_sub_line(window, line, s):
    if not s:
        return

    _, width = window.getmaxyx()
    if len(s) < width:
        print_centered(window, width, line, s)
    else:
        parts = words_and_spaces(s)
        substr = ''
        for part in parts:
            if len(substr) + len(part) < width:
                substr +=part
            else:
                print_centered(window, width, line, substr)
                line += 1
                substr = part
        print_centered(window, width, line, substr)


def print_sub(window, s):
    line = 0
    for l in s:
        print_sub_line(window, line, l)
        line = window.getyx()[0] + 1


def get_key(stdscr):
    try:
        k = stdscr.getkey()
    except curses.error:
        k = None
    return k


def main(stdscr, start, subs):
    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.nodelay(True)

    state = State(start)

    while True:
        state.handle_key_press(get_key(stdscr))

        if state.pause:
            continue

        stdscr.clear()
        height, width = stdscr.getmaxyx()

        t = now() - state.start

        s = subs.get(int(t*state.scale))
        if s:
            print_sub(stdscr, s)

        stdscr.addstr(height - 1, 0, get_time_str(t), curses.A_DIM)
        speed = '{:3.1f}x'.format(state.scale)
        stdscr.addstr(height -1, width - 5, speed, curses.A_DIM)

        curses.napms(50)


if __name__ == '__main__':
    start = now()
    subs = get_subtitles()
    curses.wrapper(main, start, subs)
