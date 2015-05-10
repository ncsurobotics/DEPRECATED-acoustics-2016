import os
import sys

base = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, base + '/../pinger_finder/bbb/')

import boot


def enable_uart():
    boot.uart()


def disable_uart():
    boot.nouart()
