from typing import Optional

from .time_utils import now

SMALL_TIME_SKIP = 5
LARGE_TIME_SKIP = 600
SCALE_STEP = 0.02


class State:
    def __init__(self, start: int, pause: Optional[int] = None, scale: float = 1) -> None:
        self._start = start
        self._pause = pause
        self.scale = scale
        self.show_info = True
        self.exit = False

    def handle_key_press(self, k: str) -> None:
        if k == 'q':
            self.exit = True
        elif k == ' ':
            if self._pause:
                self._start += now() - self._pause
                self._pause = None
            else:
                self._pause = now()
        elif k == 'a':
            self._start += SMALL_TIME_SKIP
        elif k == 'd':
            self._start -= SMALL_TIME_SKIP
        elif k == 'c':
            self.scale += SCALE_STEP
            self._adjust_start_after_rescaling(self.scale - SCALE_STEP)
        elif k == 'z':
            self.scale -= SCALE_STEP
            self._adjust_start_after_rescaling(self.scale + SCALE_STEP)
        elif k == 'w':
            self._start += LARGE_TIME_SKIP
        elif k == 'r':
            self._start -= LARGE_TIME_SKIP
        elif k == 'i':
            self.show_info = not self.show_info

    def get_current_time(self) -> int:
        _now = self._pause or now()
        return int((_now - self._start) * self.scale)

    def _adjust_start_after_rescaling(self, old_scale: float) -> None:
        _now = self._pause or now()
        self._start = int(_now - (_now - self._start) * old_scale / self.scale)

