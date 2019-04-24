#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Print
"""

printDebugMessageLevel = 0


def print_debug(curScript, curDebugMessage, curDebugMessageLevel=0):
    """
    Prindib vastava taseme täiendatavat informatsiooni, kui seda soovitakse
    """

    if (printDebugMessageLevel >= curDebugMessageLevel):
        print(curScript.split("/")[-1] + ": " + str(curDebugMessage))
