log = 'UI Initialized'


# Add message to top of log
def add_text(message):
    global log
    log = message + '\n' + log


def get_text():
    global log
    return log

