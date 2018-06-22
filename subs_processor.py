from typing import Optional, List
from time_utils import get_time_from_str


class SubsFileNotFound(Exception):
    pass


class Subs:
    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._subs_map = {}
        self._subs_list = []
        self._line_processed = 0
        self._lines = []

    def process(self) -> None:
        try:
            with open(self._filename, 'r') as f:
                self._lines = [l.strip('\n ') for l in f.readlines()]
        except FileNotFoundError:
            print('File {} cannot be found'.format(self._filename))
            raise SubsFileNotFound

        while not self._process_finished():
            self._process_next()

    def get_sub(self, t: int) -> Optional[List[str]]:
        sub_id = self._subs_map.get(t)
        if not sub_id:
            return None
        return self._subs_list[sub_id]

    def _process_finished(self) -> bool:
        return self._line_processed >= len(self._lines)

    def _get_current_line(self) -> str:
        return self._lines[self._line_processed]

    def _process_next(self) -> None:
        next_block_found = False
        sub_lines = []
        t0_ms = None
        t1_ms = None
        while not self._process_finished() and (not next_block_found or self._get_current_line()):
            if self._get_current_line():
                if not next_block_found:
                    next_block_found = True
                    self._line_processed += 1
                    t0, t1 = self._get_current_line().split(' --> ')
                    t0_ms = get_time_from_str(t0)
                    t1_ms = get_time_from_str(t1)
                else:
                    sub_lines.append(self._get_current_line())
            self._line_processed += 1

        if t0_ms and t1_ms:
            sub_id = len(self._subs_list)
            self._subs_map.update({t: sub_id for t in range(t0_ms, t1_ms + 1)})
            self._subs_list.append(sub_lines)
