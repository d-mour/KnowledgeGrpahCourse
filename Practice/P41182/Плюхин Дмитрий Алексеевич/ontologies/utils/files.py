import os

import yaml


def read_yaml(filename):
    with open(filename) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def get_yaml_files(folder: str):
    return get_all_files_with_extension(folder, 'yaml')


def read_lines(filename):
    with open(filename) as f:
        return [line.replace('\n', '') for line in f.readlines()]


def read_binary(filename):
    with open(filename, 'rb') as f:
        return f.read()


def read(filename):
    return ' '.join(read_lines(filename))


def write(filename, content):
    with open(filename, 'w') as f:
        f.write(content)


def get_all_files_with_extension(folder: str, extension: str):
    return tuple(map(
        # Get full path to the files
        lambda filename: os.path.join(folder, filename),
        filter(
            # Skip not-docx files
            lambda filename: os.path.splitext(filename)[-1] == f'.{extension}',
            os.listdir(folder)
        )
    ))
