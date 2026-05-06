def list_from_file(file_path: object):
    list = []
    with open(file_path, "r") as file:
        lines = file.read().splitlines()
        for line in lines:
            list.append(line)
    return list
