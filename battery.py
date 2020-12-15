# -*- coding: utf-8 -*-
"""Summary.

Attributes:
    BAT_A (str): Line to draw top and bottom of battery.
    BAT_B (str): Line to draw battery.
    battery_ascii (TYPE): Battery without segments.
    bufsize (TYPE): Description
    cursorInfo (TYPE): Description
    hStdOut (TYPE): Description
    NOTIFICATION (str): A notification text.
    sounds (list): List of sound files.
    STD_OUTPUT_HANDLE (int): Description
"""

from __future__ import print_function

import time
import os

from ctypes import windll, Structure, c_int, byref, wintypes
from datetime import timedelta
from datetime import datetime
from random import choice
from colorama import init
from playsound import playsound

import psutil


class ConsoleCursorInfo(Structure):
    """Cursor class with ctypes.

    Attributes:
        b_visible (int): Description
        dw_size (int): Description
    """

    def __init__(self):
        """Clas initialisation."""
        self.dw_size = 1
        self.b_visible = 0

    _fields_ = [('dw_size', c_int), ('b_visible', c_int)]


STD_OUTPUT_HANDLE = -11

hStdOut = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
cursorInfo = ConsoleCursorInfo()
bufsize = wintypes._COORD(80, 30)  # rows, columns
windll.kernel32.SetConsoleScreenBufferSize(hStdOut, bufsize)
windll.kernel32.SetConsoleCursorInfo(hStdOut, byref(cursorInfo))
windll.kernel32.SetConsoleTitleA(b'Battery monitor and alarm')

init()

sounds = ["sounds/apx_battery_low_aler.mp3",
          "sounds/battery_low.mp3",
          "sounds/galaxy_low_battery.mp3",
          "sounds/htc_one_low_battery.mp3",
          "sounds/jarvis_low_battery.mp3",
          "sounds/low_battery (1).mp3",
          "sounds/low_battery.mp3"]

NOTIFY = "Awake: {AWAKE} | Battery: {PERCENT}% | {CHARGER_STATUS}. (Remaining: {TIME})"

BAT_A = "█" * 36 + " " * 12 + "\n"
BAT_B = "█" * 2 + " " * 32 + "█" * 2 + " " * 12 + "\n"
battery_ascii = BAT_A + BAT_B + "{SEGMENTS}" + BAT_B + BAT_A

cwdth, _ = os.get_terminal_size()


def center_wrap(text, cwidth=cwdth):
    """Center the multiline text.

    Args:
        text (str): The multiline text.
        cwidth (int, optional): Console width.

    Returns:
        str: Centered to console multiline string
    """
    lines = text.split('\n')
    return "\n".join(((cwidth - len(line)) // 2 + 4) * ' '
                     + line.strip() for line in lines)


def draw_battery(percentage):
    """Draw battery ASCII art.

    Args:
        percentage (int): The battery percentage.

    Returns:
        str: Battery segments.
    """
    if percentage <= 20:
        line = "██  \033[31m████\033[39mllllllllllllllllllllllll  ████\n" * 8
    elif percentage <= 40:
        line = "██  \033[33m████ll████\033[39mllllllllllllllllll  ████\n" * 8
    elif percentage <= 60:
        line = "██  \033[33m████ll████ll████\033[39mllllllllllll  ████\n" * 8
    elif percentage <= 80:
        line = "██  \033[32m████ll████ll████ll████\033[39mllllll  ████\n" * 8
    else:
        line = "██  \033[32m████ll████ll████ll████ll████\033[39m  ████\n" * 8

    return center_wrap(battery_ascii.format(SEGMENTS=line.replace('l', '░')), 80)


print("\n" * 5)

while True:
    battery = psutil.sensors_battery()
    timeleft = timedelta(seconds=battery.secsleft)
    now = datetime.now().replace(microsecond=0)
    awaked = datetime.fromtimestamp(psutil.boot_time()).replace(microsecond=0)
    awake = now - awaked
    percent = battery.percent
    plugged = battery.power_plugged
    CHARGER_STATUS = "Plugged in" if plugged else "Unplugged"
    TEXT = NOTIFY.format(PERCENT=percent,
                         CHARGER_STATUS=CHARGER_STATUS,
                         AWAKE=awake,
                         TIME=timeleft).center(cwdth)
    print(draw_battery(percent), '\n' + TEXT)
    print('\x1b[15A', end='')

    if percent < 20 and not plugged:
        playsound(choice(sounds))
    time.sleep(1)
    os.system('echo off')
