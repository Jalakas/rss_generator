
"""
    Print.
"""

import inspect

import rss_config


def print_debug(curScript, curDebugMessage, curDebugMessageLevel):
    """
        Prindib vastava taseme täiendatavat informatsiooni, kui seda soovitakse.
    """
    if rss_config.PRINT_MESSAGE_LEVEL >= curDebugMessageLevel:
        functionName = "." + inspect.stack()[1][3] + "()"
        if functionName == ".<module>()":
            functionName = ""
        print(curScript.split("/")[-1][:-3] + functionName + ": " + curDebugMessage)
