
"""
    Erinevate aeg puudutavad parserid ja funktsioonid.
"""

import time
from datetime import datetime
from datetime import timedelta
from email.utils import formatdate
from email.utils import parsedate

import parsers_common
import rss_print


def add_missing_date_to_string(curDatetimeString, fullDatetimeFormat, addedDateFormat):
    if len(curDatetimeString) < len(fullDatetimeFormat):
        curDatetimeString = add_value_to_time_string(curDatetimeString, addedDateFormat)
        rss_print.print_debug(__file__, "lisasime ajale 'kuupäeva' osa: " + curDatetimeString, 3)

    return curDatetimeString


def add_value_to_time_string(curArtPubDate, curDateFormat, offsetDays=0):
    """
    Lisab ajale stringi.
    @curArtPubDate = nt: 03.01
    @curDateFormat = algusesse lisatav osa nt: 2019.
    @offsetDays = 0 täna, -1 eile
    """
    datetimeOffset = datetime_offset_from_format(offsetDays)

    curArtPubDate = (datetime.now() + datetimeOffset).strftime(curDateFormat) + curArtPubDate
    rss_print.print_debug(__file__, "lisasime tänasele kellaajale kuupäeva: " + curArtPubDate, 3)

    return curArtPubDate


def datetime_offset_from_format(offsetDays):
    datetimeOffset = timedelta(days=offsetDays)
    if offsetDays:
        rss_print.print_debug(__file__, "" + str(datetimeOffset), 5)

    return datetimeOffset


def float_to_datetime_rfc2822(floatDateTime):
    """
    Teeb sisse antud floadist rfc2822 aja.
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    rss_print.print_debug(__file__, "floatDateTime = '" + str(floatDateTime) + "'", 5)
    datetimeRFC2822 = formatdate(floatDateTime, True, True)
    rss_print.print_debug(__file__, "datetimeRFC2822 = '" + str(datetimeRFC2822) + "'", 4)

    return datetimeRFC2822


def guess_datetime(curArtPubDate):
    """
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior.
    """
    curArtPubDate = curArtPubDate.strip(", ")
    curArtPubDate = curArtPubDate.lower()

    # NB väiketähed, järjekord on oluline
    if len(curArtPubDate) > 10:
        if curArtPubDate.find("t") == 10:
            curArtPubDate = raw_to_datetime(curArtPubDate, "%Y-%m-%dt%H:%M:%S%z")
        elif curArtPubDate.find("am") > -1 or curArtPubDate.find("pm") > -1:
            if curArtPubDate.find("-") > -1:
                # "14-04-2020, 00:05 am" to datetime()
                curArtPubDate = raw_to_datetime(curArtPubDate, "%d-%m-%Y, %H:%M %p")
            else:
                # "06 26, 2019 8:07 pm" to datetime()
                curArtPubDate = raw_to_datetime(curArtPubDate[2:], "%m %d, %Y %I:%M %p")
        elif curArtPubDate.find("-") > -1:
            # "21-11-16, 04:11" to datetime()
            curArtPubDate = raw_to_datetime(curArtPubDate, "%d-%m-%y,%H:%M")
        elif curArtPubDate.find(". ") > -1:
            if curArtPubDate.find(",") > -1:
                # "26. 06 2019, 18:07:05" to datetime()
                curArtPubDate = raw_to_datetime(curArtPubDate, "%d. %m %Y, %H:%M:%S")
            else:
                # "01. 03 2021 14:34" to datetime()
                curArtPubDate = raw_to_datetime(curArtPubDate, "%d. %m %Y %H:%M")
        elif curArtPubDate.find("»") > -1:
            # "» 29 12 2017 13:46" to datetime()
            curArtPubDate = raw_to_datetime(curArtPubDate, "» %d %m %Y %H:%M")
        elif curArtPubDate.find(":") > -1:
            if curArtPubDate.find("t,") > -1 and curArtPubDate.find(":") > curArtPubDate.find(","):
                # "09 02 t, 2021 14:39" to datetime()
                curArtPubDate = raw_to_datetime(curArtPubDate, "%d %m t, %Y %H:%M")
            elif curArtPubDate.find(",") > -1 and curArtPubDate.find(":") > curArtPubDate.find(","):
                if curArtPubDate.find(",") >= 10:
                    # "16 10 2019, 20:53" to datetime()
                    curArtPubDate = raw_to_datetime(curArtPubDate, "%d %m %Y, %H:%M")
                else:
                    # "03 03, 2019 16:26" to datetime()
                    curArtPubDate = raw_to_datetime(curArtPubDate, "%d %m, %Y %H:%M")
            elif curArtPubDate.find(",") > curArtPubDate.find(":"):
                # "15:36, 09 05 2020" to datetime()
                curArtPubDate = raw_to_datetime(curArtPubDate, "%H:%M, %d %m %Y")
            elif curArtPubDate.find(".") > -1:
                # "09.10.2019 18:43" to datetime()
                curArtPubDate = raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")
            else:
                # "09 10 2019 18:43" to datetime()
                curArtPubDate = raw_to_datetime(curArtPubDate, "%d %m %Y %H:%M")
    elif len(curArtPubDate) <= 10:
        # "09.10.2019" to datetime()
        curArtPubDate = raw_to_datetime(curArtPubDate, "%d.%m.%Y")

    return curArtPubDate


def increasing_datetime_rfc2822(firstDatetimeRfc2822, secondDatetimeRfc2822):
    time1 = parsedate(firstDatetimeRfc2822)
    time2 = parsedate(secondDatetimeRfc2822)
    if time2 >= time1:
        return True

    return False


def months_to_int(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.lower()
    # est long
    rawDateTimeText = rawDateTimeText.replace('jaanuar', '01').replace('veebruar', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
    rawDateTimeText = rawDateTimeText.replace('juuli', '07').replace('august', '08').replace('september', '09').replace('oktoober', '10').replace('november', '11').replace('detsember', '12')
    # est short
    rawDateTimeText = rawDateTimeText.replace('jaan', '01').replace('veebr', '02').replace('veeb', '02').replace('märts', '03').replace('mär', '03')
    rawDateTimeText = rawDateTimeText.replace('aprill', '04').replace('mai', '05').replace('juun', '06')
    rawDateTimeText = rawDateTimeText.replace('juul', '07').replace('aug', '08').replace('sept', '09')
    rawDateTimeText = rawDateTimeText.replace('okt', '10').replace('nov', '11').replace('dets', '12')
    # eng short
    rawDateTimeText = rawDateTimeText.replace('jan', '01').replace('feb', '02').replace('mar', '03').replace('apr', '04').replace('may', '05').replace('jun', '06')
    rawDateTimeText = rawDateTimeText.replace('jul', '07').replace('aug', '08').replace('sep', '09').replace('oct', '10').replace('nov', '11').replace('dec', '12')

    return rawDateTimeText


def raw_to_datetime(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sisseantud ajatekstist ja süntaksist datetime tüüpi aja.
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    curDateTimeText = rawDateTimeText
    curDateTimeText = curDateTimeText.strip()
    curDateTimeText = parsers_common.str_lchop(curDateTimeText, "\\t")
    curDateTimeText = parsers_common.str_rchop(curDateTimeText, "\\r\\n")

    if not curDateTimeText:
        rss_print.print_debug(__file__, "tühi ajasisend: curDateTimeText = '" + curDateTimeText + "'", 0)
    else:
        rss_print.print_debug(__file__, "curDateTimeText = '" + curDateTimeText + "'", 5)

    if not rawDateTimeSyntax:
        rss_print.print_debug(__file__, "tühi ajasisend: rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 0)
    else:
        rss_print.print_debug(__file__, "rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 5)

    datetimeFloat = raw_to_float(curDateTimeText, rawDateTimeSyntax)
    datetimeRFC2822 = float_to_datetime_rfc2822(datetimeFloat)

    return datetimeRFC2822


def raw_to_datetime_guess_missing(inpArtPubDate, lastArtPubDate, dateStringPrefix, dateStringMain, daysToOffset):
    curOffsetDays = 0
    curArtPubDate = inpArtPubDate

    curArtPubDate = add_value_to_time_string(curArtPubDate, dateStringPrefix, curOffsetDays)
    curArtPubDate = raw_to_datetime(curArtPubDate, dateStringPrefix + dateStringMain)
    if lastArtPubDate and not increasing_datetime_rfc2822(curArtPubDate, lastArtPubDate):
        rss_print.print_debug(__file__, "uudise päev: täna " + str(curArtPubDate) + " ja eile " + str(lastArtPubDate), 3)
        rss_print.print_debug(__file__, "esineb ajahüpe, peame muutma tambovi lisamise offsetti", 3)
        curOffsetDays += daysToOffset
        curArtPubDate = inpArtPubDate
        curArtPubDate = add_value_to_time_string(curArtPubDate, dateStringPrefix, curOffsetDays)
        curArtPubDate = raw_to_datetime(curArtPubDate, dateStringPrefix + dateStringMain)
        rss_print.print_debug(__file__, "uudise eelmine päev: " + str(lastArtPubDate), 3)
        rss_print.print_debug(__file__, "uudise praegune päev muutus: " + inpArtPubDate + " -> " + str(curArtPubDate), 2)
    else:
        rss_print.print_debug(__file__, "uudise päev: täna " + str(curArtPubDate) + " ja eile " + str(lastArtPubDate), 4)

    return curArtPubDate


def raw_to_float(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sisseantud ajatekstist ja süntaksist float tüüpi aja.
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    curDateTimeText = rawDateTimeText.strip()
    if not curDateTimeText:
        rss_print.print_debug(__file__, "curDateTimeText = '" + curDateTimeText + "' tühi, tagastame nulli", 0)
        return 0

    try:
        datetimeStruct = time.strptime(curDateTimeText, rawDateTimeSyntax)
        datetimeList = list(datetimeStruct)

        if datetimeList[0] == 1900:
            if datetimeList[1] > int(time.strftime('%m')):
                rss_print.print_debug(__file__, "curDateTimeText = '" + curDateTimeText + "', muudame puuduva aasta eelmiseks aastaks", 0)
                datetimeList[0] = int(time.strftime('%Y')) - 1
            else:
                rss_print.print_debug(__file__, "curDateTimeText = '" + curDateTimeText + "', muudame puuduva aasta praeguseks aastaks", 0)
                datetimeList[0] = int(time.strftime('%Y'))

        datetimeTuple = tuple(datetimeList)
        datetimeFloat = time.mktime(datetimeTuple)
    except Exception as e:
        rss_print.print_debug(__file__, "curDateTimeText = '" + curDateTimeText + "' dekodeerimine rawDateTimeSyntax = '" + rawDateTimeSyntax + "' EBAõnnestus, tagastame nulli", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        return 0

    return datetimeFloat


def remove_weekday_strings(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.lower()
    # est
    rawDateTimeText = rawDateTimeText.replace('esmaspäev', "").replace('teisipäev', "").replace('kolmapäev', "")
    rawDateTimeText = rawDateTimeText.replace('neljapäev', "").replace('reede', "").replace('laupäev', "").replace('pühapäev', "")

    return rawDateTimeText


def replace_string_with_timeformat(inpString, stringToReplace, dateTimeformat, offsetDays=0):
    """
    Asendab sisendis etteantud stringi mingit formaati ajaga.
    Sisendid:
        inpString="eile, 23:34"
        stringToReplace="eile",
        dateTimeformat="%d %m %Y",
        offsetDays=-1
    Väljund: 24 05 2020, 23:34
    """
    if stringToReplace in inpString:
        datetimeOffset = datetime_offset_from_format(offsetDays)
        inpString = inpString.replace(stringToReplace, str((datetime.now() + datetimeOffset).strftime(dateTimeformat)))
        rss_print.print_debug(__file__, "asendasime stringis sõna ajaga: '" + stringToReplace + "' -> " + inpString, 3)

    return inpString


def time_float():
    curTimeFloat = time.time()

    return curTimeFloat
