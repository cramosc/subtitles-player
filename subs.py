import argparse
import curses
from time import sleep, time

import sys


def get_time(t):
    t = t.split(':')
    return int((int(t[0])*3600 + int(t[1])*60 + float(t[2].replace(',', '.')))*10)


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
                t0_ms = get_time(t0)
                t1_ms = get_time(t1)
            else:
                sub_lines.append(lines[line_no])
        line_no += 1

    sub_str = '\n'.join(sub_lines)
    sub = {}
    if t0_ms and t1_ms:
        sub = {t: sub_str for t in range(t0_ms, t1_ms + 1)}
    return sub, line_no


def get_subtitles():
    parser = argparse.ArgumentParser(description='Display subtitles from file in a dark background')
    parser.add_argument('file', type=str, help='file path')

    options = parser.parse_args()

    with open(options.file, 'r') as f:
        lines = [l.strip('\n') for l in f.readlines()]

    subs = {}
    line_no = 0
    while line_no < len(lines):
        sub, line_no = get_sub(line_no, lines)
        subs.update(sub)

    return subs


def get_time_str(t):
    t = t // 10
    h = t // 3600
    t = t % 3600
    m = t // 60
    t = t % 60
    return ':'.join([str(i).zfill(2) for i in (h,m,t)])


def get_key(stdscr):
    try:
        k = stdscr.getkey()
    except:
        k = None
    return k


def main(stdscr, start):
    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.nodelay(True)

    scale = 1.0

    subs = get_subtitles()

    stop = None

    while True:
        k = get_key(stdscr)
        if k == 'q':
            sys.exit(0)
        elif k == ' ':
            if stop:
                start += now() - stop
                stop = None
            else:
                stop = now()
        elif k == 'a':
            start += 5
        elif k == 'd':
            start -= 5
        elif k == 'z':
            scale += 0.1
        elif k == 'c':
            scale -= 0.1
        elif k == 'q':
            start += 500
        elif k == 'e':
            start -= 500

        if stop:
            continue

        stdscr.clear()

        t = now() - start
        s = subs.get(int(t*scale))
        if s:
            stdscr.addstr(0, 0, s, curses.A_BOLD)
        height, width = stdscr.getmaxyx()
        stdscr.addstr(height - 1, 0, get_time_str(t), curses.A_DIM)
        speed = '{:3.1f}x'.format(scale)
        stdscr.addstr(height -1, width - 5, speed, curses.A_DIM)
        sleep(.1)


def now():
    return int(time() * 10)


if __name__ == '__main__':
    curses.wrapper(main, now())
