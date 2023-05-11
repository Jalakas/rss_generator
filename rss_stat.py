
import fileinput
import sys

import rss_print


def save_string_stat(filename, saveToFile, inpString, found):

    if saveToFile is True:
        countFound = 0
        countNotFound = 0
        inpString = inpString.replace("/./", "/")

        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith(inpString):
                        splittedLine = line.split(";")
                        countFound = (int)(splittedLine[1])
                        countNotFound = (int)(splittedLine[2])
        except Exception:
            with open(filename, "a", encoding="utf-8") as file:
                file.write("")

        if found:
            countFound += 1
        else:
            countNotFound += 1

        inpStringWithStats = inpString + ";" + str(countFound) + ";" + str(countNotFound) + ";"
        inpStringWithStats = inpStringWithStats.replace("/./", "/")

        replace_line_in_file(filename, inpString + ";", inpStringWithStats)


def replace_line_in_file(filename, searchExp, replaceExp):

    found = False

    for line in fileinput.input(filename, inplace=1):
        if line.startswith(searchExp):
            found = True
            line = replaceExp + "\n"
        sys.stdout.write(line)

    if not found:
        rss_print.print_debug(__file__, "lisame faili lõppu: " + replaceExp, 2)
        with open(filename, "a", encoding="utf-8") as file:
            file.write(replaceExp + "\n")
