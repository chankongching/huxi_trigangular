import logging


# from apps.statistics.rstats import RStats
# class NullHandler(logging.Handler):  # exists in python 3.1
#     def emit(self, record):
#         pass


def getlogger():
    logger = logging.getLogger('default')
    return logger


def debug(msg, *args, **kwargs):
    logger = getlogger()
    logger.debug(colorize(msg, *args, **kwargs))


def info(msg, *args, **kwargs):
    logger = getlogger()
    logger.info(colorize(msg, *args, **kwargs))


def error(msg, *args, **kwargs):
    logger = getlogger()
    logger.error(msg, *args, **kwargs)


def colorize(msg, *args, **kwargs):
    # params = {
    #     r'\-\-\->': '~FB~SB--->~FW',
    #     r'\*\*\*>': '~FB~SB~BB--->~BT~FW',
    #     r'\[': '~SB~FB[~SN~FM',
    #     r'AnonymousUser': '~FBAnonymousUser',
    #     r'\*(\s*)~FB~SB\]': r'~SN~FR*\1~FB~SB]',
    #     r'\]': '~FB~SB]~FW~SN',
    # }
    # colors = {
    #     '~SB': Style.BRIGHT,
    #     '~SN': Style.NORMAL,
    #     '~SK': Style.BLINK,
    #     '~SU': Style.UNDERLINE,
    #     '~ST': Style.RESET_ALL,
    #     '~FK': Fore.BLACK,
    #     '~FR': Fore.RED,
    #     '~FG': Fore.GREEN,
    #     '~FY': Fore.YELLOW,
    #     '~FB': Fore.BLUE,
    #     '~FM': Fore.MAGENTA,
    #     '~FC': Fore.CYAN,
    #     '~FW': Fore.WHITE,
    #     '~FT': Fore.RESET,
    #     '~BK': Back.BLACK,
    #     '~BR': Back.RED,
    #     '~BG': Back.GREEN,
    #     '~BY': Back.YELLOW,
    #     '~BB': Back.BLUE,
    #     '~BM': Back.MAGENTA,
    #     '~BC': Back.CYAN,
    #     '~BW': Back.WHITE,
    #     '~BT': Back.RESET,
    # }
    # for k, v in params.items():
    #     msg = re.sub(k, v, msg)
    # msg = msg + '~ST~FW~BT'
    # # msg = re.sub(r'(~[A-Z]{2})', r'%(\1)s', msg)
    # for k, v in colors.items():
    #     msg = msg.replace(k, v)
    return msg, args, kwargs


'''
This module generates ANSI character codes to printing colors to terminals.
See: http://en.wikipedia.org/wiki/ANSI_escape_code
'''

COLOR_ESC = '\033['


class AnsiCodes(object):
    def __init__(self, codes):
        for name in dir(codes):
            if not name.startswith('_'):
                value = getattr(codes, name)
                setattr(self, name, COLOR_ESC + str(value) + 'm')


class AnsiFore:
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39


class AnsiBack:
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    RESET = 49


class AnsiStyle:
    BRIGHT = 1
    DIM = 2
    UNDERLINE = 4
    BLINK = 5
    NORMAL = 22
    RESET_ALL = 0


Fore = AnsiCodes(AnsiFore)
Back = AnsiCodes(AnsiBack)
Style = AnsiCodes(AnsiStyle)
