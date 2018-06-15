import argparse
import curses
import itertools
import sys
from time import time
from typing import List, Tuple, Dict, Optional

SubsMap = Dict[int, List[str]]


class State:
    def __init__(self, start: int, pause: Optional[int] = None, scale: float = 1) -> None:
        self.start = start
        self.pause = pause
        self.scale = scale
        self.show_info = True

    def handle_key_press(self, k: str) -> None:
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
        elif k == 'c':
            self.scale += 0.05
            self._adjust_start_after_rescaling(self.scale - 0.05)
        elif k == 'z':
            self.scale -= 0.05
            self._adjust_start_after_rescaling(self.scale + 0.05)
        elif k == 'w':
            self.start += 600
        elif k == 'r':
            self.start -= 600
        elif k == 'i':
            self.show_info = not self.show_info

    def get_current_time(self) -> int:
        _now = self.pause or now()
        return int((_now - self.start)*self.scale)

    def _adjust_start_after_rescaling(self, old_scale: float) -> None:
        _now = self.pause or now()
        self.start = int(_now - (_now - self.start)*old_scale/self.scale)


def get_time_from_str(t: str) -> int:
    t = t.split(':')
    return int((int(t[0])*3600 + int(t[1])*60 + float(t[2].replace(',', '.')))*10)


def now() -> int:
    return int(time() * 10)


def get_time_str(t: int) -> str:
    t = t // 10
    h = t // 3600
    t = t % 3600
    m = t // 60
    t = t % 60
    return ':'.join([str(i).zfill(2) for i in (h,m,t)])


def get_sub(line_no: int, lines: List[str]) -> Tuple[SubsMap, int]:
    next_block_found = False
    sub_lines = []
    t0_ms = None
    t1_ms = None
    while line_no < len(lines) and (not next_block_found or lines[line_no]):
        if lines[line_no]:
            if not next_block_found:
                next_block_found = True
                line_no += 1
                t0, t1 = lines[line_no].split(' --> ')
                t0_ms = get_time_from_str(t0)
                t1_ms = get_time_from_str(t1)
            else:
                sub_lines.append(lines[line_no])
        line_no += 1

    sub = {}
    if t0_ms and t1_ms:
        sub = {t: sub_lines for t in range(t0_ms, t1_ms + 1)}
    return sub, line_no


def get_subtitles(file: str) -> SubsMap:
    try:
        with open(file, 'r') as f:
            lines = [l.strip('\n') for l in f.readlines()]
    except FileNotFoundError:
        print('File {} cannot be found'.format(file))
        sys.exit(1)

    subs = {}
    line_no = 0
    while line_no < len(lines):
        sub, line_no = get_sub(line_no, lines)
        subs.update(sub)

    return subs


def words_and_spaces(s: str) -> List[str]:
    return list(itertools.chain.from_iterable(zip(s.split(), itertools.repeat(' '))))[:-1]


def print_centered(window, width: int, line: int, s: str) -> None:
    window.addstr(line, max(0, (width - len(s))//2), s, curses.A_BOLD)


def print_sub_line(window, line: int, s: str) -> None:
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


def print_sub(window, s: List[str]) -> None:
    line = 0
    for l in s:
        print_sub_line(window, line, l)
        line = window.getyx()[0] + 1


def get_key(stdscr) -> Optional[str]:
    try:
        k = stdscr.getkey()
    except curses.error:
        k = None
    return k


def ui_loop(stdscr, start: int, subs: SubsMap) -> None:
    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.nodelay(True)

    state = State(start)

    while True:
        state.handle_key_press(get_key(stdscr))

        stdscr.clear()
        height, width = stdscr.getmaxyx()

        t = state.get_current_time()

        s = subs.get(t)
        if s:
            print_sub(stdscr, s)

        if state.show_info:
            stdscr.addstr(height - 1, 0, get_time_str(t), curses.A_DIM)
            speed = '{:4.2f}x'.format(state.scale)
            stdscr.addstr(height -1, width - 6, speed, curses.A_DIM)

        curses.napms(50)


def main() -> None:
    start = now()
    parser = argparse.ArgumentParser(description='Display subtitles from file in a dark background')
    parser.add_argument('file', type=str, help='file path')

    options = parser.parse_args()
    subs = get_subtitles(options.file)

    curses.wrapper(ui_loop, start, subs)


if __name__ == '__main__':
    main()
