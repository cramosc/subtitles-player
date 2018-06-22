#!/usr/bin/env python3.5
import argparse
import sys

from app import App
from time_utils import now
from subs_processor import Subs, SubsFileNotFound


def main() -> int:
    start = now()
    parser = argparse.ArgumentParser(description='Display subtitles from file')
    parser.add_argument('file', type=str, help='file path')

    options = parser.parse_args()
    subs = Subs(options.file)
    try:
        subs.process()
    except SubsFileNotFound:
        return 1

    app = App(start, subs)
    return app.run()


if __name__ == '__main__':
    sys.exit(main())
