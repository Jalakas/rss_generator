
import fileinput
import sys

import rss_config
import rss_print


def save_path(count, xpathString, found):

    if count is True:
        countFound = 0
        countNotfound = 0

        try:
            with open(rss_config.PATH_FILENAME_STAT, "r") as file:
                for line in file:
                    if line.startswith(xpathString):
                        splittedLine = line.split(";")
                        countFound = (int)(splittedLine[1])
                        countNotfound = (int)(splittedLine[2])
        except Exception:
            with open(rss_config.PATH_FILENAME_STAT, 'a') as file:
                file.write("")

        if found:
            countFound += 1
        elif not found:
            countNotfound += 1

        xpathStringWithStats = xpathString + ";" + str(countFound) + ";" + str(countNotfound) + ";"

        replace_line_in_file(rss_config.PATH_FILENAME_STAT, xpathString + ";", xpathStringWithStats)

        rss_print.print_debug(__file__, xpathStringWithStats, 4)


def replace_line_in_file(inpfile, searchExp, replaceExp):

    found = False

    for line in fileinput.input(inpfile, inplace=1):
        if line.startswith(searchExp):
            found = True
            line = replaceExp + "\n"
        sys.stdout.write(line)

    if not found:
        rss_print.print_debug(__file__, "lisame lõppu: " + replaceExp, 1)
        with open(inpfile, 'a') as file:
            file.write(replaceExp + "\n")
