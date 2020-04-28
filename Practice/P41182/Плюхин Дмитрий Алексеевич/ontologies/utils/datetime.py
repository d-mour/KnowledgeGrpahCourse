from datetime import datetime


def parse_time(time: str):
    return datetime.strptime(time, '%H:%M:%S')
