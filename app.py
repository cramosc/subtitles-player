import curses
from itertools import chain, repeat
from typing import List, Optional

from state import State
from subs_processer import Subs
from time_utils import get_time_str


class App:
    def __init__(self, start: int, subs: Subs) -> None:
        self._window = None
        self._state = State(start)
        self._subs = subs

    def _init_window(self, window):
        curses.curs_set(0)
        curses.use_default_colors()
        window.nodelay(True)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self._window = window

    @staticmethod
    def _words_and_spaces(text: str) -> List[str]:
        return list(chain.from_iterable(zip(text.split(), repeat(' '))))[:-1]

    @property
    def _width(self):
        _, width = self._window.getmaxyx()
        return width

    @property
    def _height(self):
        height, _ = self._window.getmaxyx()
        return height

    def _print_centered(self, line: int, text: str) -> None:
        self._window.addstr(line, max(0, (self._width - len(text)) // 2), text, curses.A_BOLD | curses.color_pair(1))

    def _get_lines_adapted_to_width(self, text: str) -> List[str]:
        if not text:
            return []

        if len(text) < self._width:
            return [text]

        parts = self._words_and_spaces(text)
        lines = []
        sub_str = ''
        for part in parts:
            if len(sub_str) + len(part) < self._width:
                sub_str += part
            else:
                lines.append(sub_str)
                sub_str = part
        lines.append(sub_str)
        return lines

    def _print_sub(self, subtitle: List[str]) -> None:
        height, width = self._window.getmaxyx()
        lines = list(chain.from_iterable(self._get_lines_adapted_to_width(text) for text in subtitle))
        height -= 1
        for text in reversed(lines):
            height -= 1
            self._print_centered(height, text)

    def _get_key(self) -> Optional[str]:
        try:
            k = self._window.getkey()
        except curses.error:
            k = None
        return k

    def run(self) -> int:
        return curses.wrapper(self._run)

    def _run(self, window) -> int:
        self._init_window(window)

        while True:
            self._state.handle_key_press(self._get_key())
            if self._state.exit:
                return 0

            self._window.clear()
            current_time = self._state.get_current_time()

            sub = self._subs.get_sub(current_time)
            if sub:
                self._print_sub(sub)

            if self._state.show_info:
                self._window.addstr(0, 0, get_time_str(current_time), curses.A_DIM | curses.color_pair(1))
                speed = '{:4.2f}x'.format(self._state.scale)
                self._window.addstr(0, self._width - 5, speed, curses.A_DIM | curses.color_pair(1))

            curses.napms(50)
