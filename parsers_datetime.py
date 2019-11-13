#!/usr/bin/env python3

"""
    Erinevate aeg puudutavad parserid ja funktsioonid
"""

from datetime import datetime
from datetime import timedelta
from email import utils
import time

import parsers_common
import rss_print


def add_missing_date_to_string(curDatetimeString, fullDatetimeFormat, addedDateFormat):
    if len(curDatetimeString) < len(fullDatetimeFormat):
        curDatetimeString = add_to_time_string(curDatetimeString, addedDateFormat)
        rss_print.print_debug(__file__, "lisasime ajale 'kuupäeva' osa: " + curDatetimeString, 3)

    return curDatetimeString


def add_to_time_string(curArtPubDate, curDateFormat):
    curArtPubDate = datetime.now().strftime(curDateFormat) + curArtPubDate.strip()
    rss_print.print_debug(__file__, "lisasime tänasele kellaajale kuupäeva: " + curArtPubDate, 3)

    return curArtPubDate


def guess_datetime(curArtPubDate):
    # NB järjekord on oluline

    if curArtPubDate.find("-") >= 0:
        # timeformat magic from "21-11-16, 04:11" to datetime()
        curArtPubDate = raw_to_datetime(curArtPubDate, "%d-%m-%y,%H:%M")
    elif curArtPubDate.find(".") >= 0 and curArtPubDate.find(",") >= 0:
        # timeformat magic from "26. 06 2019, 18:07:05" to datetime()
        curArtPubDate = raw_to_datetime(curArtPubDate, "%d. %m %Y, %H:%M:%S")
    elif (curArtPubDate.find("am") >= 0 or curArtPubDate.find("pm") >= 0):
        # timeformat magic from "06 26, 2019 8:07 pm" to datetime()
        curArtPubDate = raw_to_datetime(curArtPubDate[2:], "%m %d, %Y %I:%M %p")
    elif curArtPubDate.find("»") >= 0:
        # timeformat magic from "» 29 12 2017 13:46" to datetime()
        curArtPubDate = raw_to_datetime(curArtPubDate, "» %d %m %Y %H:%M")
    elif curArtPubDate.find(",") >= 10:
        # timeformat magic from "16 10 2019, 20:53" to datetime()
        curArtPubDate = raw_to_datetime(curArtPubDate, "%d %m %Y, %H:%M")
    elif curArtPubDate.find(",") >= 0:
        # timeformat magic from "03 03, 2019 16:26" to datetime()
        curArtPubDate = raw_to_datetime(curArtPubDate, "%d %m, %Y %H:%M")
    else:
        # timeformat magic from "09.10.2019 18:43" to datetime()
        curArtPubDate = raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")

    return curArtPubDate


def float_to_datetime(floatDateTime, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    rss_print.print_debug(__file__, "floatDateTime = '" + str(floatDateTime) + "'", 5)
    rss_print.print_debug(__file__, "rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 5)
    datetimeRFC2822 = utils.formatdate(floatDateTime, True, True)
    rss_print.print_debug(__file__, "datetimeRFC2822 = '" + str(datetimeRFC2822) + "'", 4)

    return datetimeRFC2822


def raw_to_datetime(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sisseantud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    curDateTimeText = rawDateTimeText
    curDateTimeText = curDateTimeText.strip()
    curDateTimeText = parsers_common.lchop(curDateTimeText, "\\t")
    curDateTimeText = parsers_common.rchop(curDateTimeText, "\\r\\n")

    if curDateTimeText == "":
        rss_print.print_debug(__file__, "ajasisend tühi: curDateTimeText = '" + curDateTimeText + "'", 0)
    else:
        rss_print.print_debug(__file__, "curDateTimeText = '" + curDateTimeText + "'", 5)

    if rawDateTimeSyntax == "":
        rss_print.print_debug(__file__, "ajasisend tühi: rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 0)
    else:
        rss_print.print_debug(__file__, "rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 5)

    datetimeFloat = raw_to_float(curDateTimeText, rawDateTimeSyntax)
    datetimeRFC2822 = float_to_datetime(datetimeFloat, rawDateTimeSyntax)

    return datetimeRFC2822


def raw_to_float(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist float tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    curDateTimeText = rawDateTimeText.strip()
    if curDateTimeText == "":
        rss_print.print_debug(__file__, "ajasisend tühi: curDateTimeText = '" + curDateTimeText + "'", 0)
        return 0

    datetimeStruct = time.strptime(curDateTimeText, rawDateTimeSyntax)
    datetimeList = list(datetimeStruct)

    if datetimeList[0] == 1900:
        if datetimeList[1] > int(time.strftime('%m')):
            rss_print.print_debug(__file__, "muudame puuduva aasta eelmiseks aastaks", 0)
            datetimeList[0] = int(time.strftime('%Y')) - 1
        else:
            rss_print.print_debug(__file__, "muudame puuduva aasta praeguseks aastaks", 0)
            datetimeList[0] = int(time.strftime('%Y'))

    datetimeTuple = tuple(datetimeList)
    datetimeFloat = time.mktime(datetimeTuple)

    return datetimeFloat


def replace_string_with_timeformat(inpString, stringToReplace, dateTimeformat, offSetDays=0):
    if stringToReplace in inpString:
        inpString = inpString.replace(stringToReplace, str((datetime.now() + timedelta(days=offSetDays)).strftime(dateTimeformat)))
        rss_print.print_debug(__file__, "asendasime stringis sõna ajaga: '" + stringToReplace + "' -> " + inpString, 3)

    return inpString


def time_float():
    curTimeFloat = time.time()

    return curTimeFloat
