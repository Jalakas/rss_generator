#!/usr/bin/env python3

import fileinput
import sys

import rss_config
import rss_print


def save_path(count, xpathString, found):

    if count is True:
        countFound = 0
        countNotfound = 0

        file = open(rss_config.PATH_FILENAME_STAT, "r")
        for line in file:
            if line.startswith(xpathString):
                splittedLine = line.split(";")
                countFound = (int)(splittedLine[1])
                countNotfound = (int)(splittedLine[2])

        if found is True:
            countFound += 1
        elif found is False:
            countNotfound += 1

        xpathStringWithStats = xpathString + ";" + str(countFound) + ";" + str(countNotfound) + ";"

        replace_line_in_file(rss_config.PATH_FILENAME_STAT, xpathString + ";", xpathStringWithStats)

        # print
        rss_print.print_debug(__file__, xpathStringWithStats, 4)


def replace_line_in_file(inpfile, searchExp, replaceExp):

    found = False

    for line in fileinput.input(inpfile, inplace=1):
        if line.startswith(searchExp):
            found = True
            line = replaceExp + "\n"
        sys.stdout.write(line)

    if found is False:
        rss_print.print_debug(__file__, "lisame lõppu: " + replaceExp, 1)
        with open(inpfile, 'a') as file:
            file.write(replaceExp + "\n")
