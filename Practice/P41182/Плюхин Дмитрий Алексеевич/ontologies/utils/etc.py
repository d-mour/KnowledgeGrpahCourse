from time import time


def stringify_marked_reviewable(target: str, year: int, mark: int) -> str:
    return f'{target.split("/")[-1]:20s}{year:10s}{mark:10s}'


def print_elapsed_time(start_time):
    print(f'Took {time() - start_time:0.10f} seconds')
