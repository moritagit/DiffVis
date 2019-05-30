# -*- coding: utf-8 -*-


import html
import unicodedata


def _get_char_width(char):
    char_type = unicodedata.east_asian_width(char)
    if char_type in ['W', 'F']:
        return 2
    else:
        return 1


def _pad_letter(letter):
    if letter in ['', ' ']:
        # zenkaku space
        return '　'
    elif _get_char_width(letter) == 1:
        return ' ' + letter
    else:
        return letter


def _pad_sequence(text, length=0):
    result = []
    if text:
        for letter in text:
            result.append(_pad_letter(letter))
    else:
        result.append(_pad_letter(text))
    if length:
        result += ['　'] * (length - len(result))
    result = ''.join(result)
    return result


class Formatter(object):
    def escape(self, text):
        """Escape special sequence."""
        return text

    def pad(self, text, length=0):
        """Pad sequence."""
        return text

    def colorize(self, text, color):
        """Colorize text."""
        return text

    def form(self, text):
        """Arange."""
        return text

    def concatenate(self, text1, text2):
        """Concatenate outputs for comparison."""
        return '\n'.join([text1, text2])


class HTMLFormatter(Formatter):
    COLOR_CODE = [
        'black',
        'green',
        'red',
        'yellow',
        'blue',
        'purple',
        'cyan',
        'white',
    ]
    def escape(self, text):
        text = html.escape(text)
        return text

    def pad(self, text, length=0):
        return _pad_sequence(text, length)

    def colorize(self, text, color):
        color_code = color.lower()
        if color_code not in HTMLFormatter.COLOR_CODE:
            raise ValueError(f'Invalid Color: {color}')
        text = f'<span style="color: {color_code};">{text}</span>'
        return text

    def concatenate(self, text1, text2):
        text = f'{text1}<br>{text2}'
        return text


class HTMLTabFormatter(Formatter):
    COLOR_CODE = [
        'black',
        'green',
        'red',
        'yellow',
        'blue',
        'purple',
        'cyan',
        'white',
    ]
    def escape(self, text):
        text = html.escape(text)
        return text

    def colorize(self, text, color):
        color_code = color.lower()
        if color_code not in HTMLTabFormatter.COLOR_CODE:
            raise ValueError(f'Invalid Color: {color}')
        text = f'<span style="color: {color_code};">{text}</span>'
        return text

    def form(self, text):
        text = f'<td style="text-align=center">{text}</td>'
        return text

    def concatenate(self, text1, text2):
        text = f'<tr>{text1}</tr><tr>{text2}</tr>'
        text = f'<table style="table-layout: fixed;">{text}</table>'
        return text


class ConsoleFormatter(Formatter):
    COLOR_CODE = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'purple': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'end': '\033[0m',
        'bold': '\038[1m',
        'underline': '\033[4m',
        'invisible': '\033[08m',
        'reverse': '\033[07m',
        }
    def pad(self, text, length=0):
        return _pad_sequence(text, length)

    def colorize(self, text, color):
        color_code = color.lower()
        if color_code not in ConsoleFormatter.COLOR_CODE:
            raise ValueError(f'Invalid Color: {color}')
        text = ConsoleFormatter.COLOR_CODE[color_code] + text + ConsoleFormatter.COLOR_CODE['end']
        return text

    def form(self, text):
        return text

    def concatenate(self, text1, text2):
        return '\n'.join([text1, text2])
