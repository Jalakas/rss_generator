#!/usr/bin/env python3

"""
    Print
"""

PRINT_MESSAGE_LEVEL = 0


def print_debug(curScript, curDebugMessage, curDebugMessageLevel):
    """
    Prindib vastava taseme täiendatavat informatsiooni, kui seda soovitakse
    """

    if PRINT_MESSAGE_LEVEL >= curDebugMessageLevel:
        print(curScript.split("/")[-1][:-3] + ": " + str(curDebugMessage))
