#!/usr/bin/env python3

"""
    RSS voogude genereerimise valikute töötleja
"""

import rss_config
import rss_print


def user_inputs(sysArgv, rssDefinitions):
    rssGenerations = []

    for i in range(1, len(sysArgv)):
        curSisend = str(sysArgv[i])
        curSisendArg = curSisend.split("=")[0]

        if curSisendArg == "-limit":
            rss_config.MAX_ARTICLE_BODIES = int(curSisend.split("=")[1])
            rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
        elif curSisend == "-nocache":
            rss_config.ARTICLE_CACHE_POLICY = 'off'
            rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
        elif curSisend == "-cache":
            rss_config.ARTICLE_CACHE_POLICY = 'all'
            rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
        elif curSisend == "-v":
            rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 1)
            rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
        elif curSisend == "-vv":
            rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 2)
            rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
        elif curSisend == "-vvv":
            rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 3)
            rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
        elif curSisend == "-vvvv":
            rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 4)
            rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
        elif curSisend == "-vvvvv":
            rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 5)
            rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
        elif curSisend != "":
            for j, rssDef in enumerate(rssDefinitions):
                if curSisend == rssDef[1]:
                    rssGenerations.append(j)
                    rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 1)
                    # tühjendame hilisema kontrolli jaoks
                    curSisend = ""
                    break
            # kui for-is ei leitud
            if curSisend != "":
                rss_print.print_debug(__file__, 'tundmatu sisend: "' + curSisend + '"', 0)

    return rssGenerations
