INPUT_PROMPT = '>'


def get_option(header='', options=[]):
    print(f'{header}:')
    for opt, name in enumerate(options, start=1):
        print(f'{opt}. {name}')
    index = int(input(INPUT_PROMPT)) - 1

    if index < 0 or index > len(options):
        raise Exception(f'Wrong argument in {header}')

    return options[index]


def get_string(header=''):
    result = input(f'{header}:')
    if not result:
        raise Exception(f'Wrong value of {header}')
    return result