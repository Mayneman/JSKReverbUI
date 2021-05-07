log = 'UI Initialized'


def add_text(message):
    global log
    log += '\n' + message


def get_text():
    global log
    return log

