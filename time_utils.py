from time import time

TIME_ACCURACY = 10


def get_time_from_str(t: str) -> int:
    h, m, s = t.split(':')
    h, m, s = int(h), int(m), float(s.replace(',', '.'))
    return int((h*3600 + m*60 + s)*TIME_ACCURACY)


def now() -> int:
    return int(time() * TIME_ACCURACY)


def get_time_str(t: int) -> str:
    t = t // TIME_ACCURACY
    h = t // 3600
    t = t % 3600
    m = t // 60
    t = t % 60
    return ':'.join([str(i).zfill(2) for i in (h,m,t)])