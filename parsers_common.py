#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Erinevate parserid ja funktsioonid
"""

import hashlib
import time
import re
from datetime import datetime, timedelta
from email import utils
from lxml import html
import lxml

import rss_makereq
import rss_print


def add_to_time_string(curArtPubDate, curDateFormat):
    curArtPubDate = datetime.now().strftime(curDateFormat) + curArtPubDate
    rss_print.print_debug(__file__, "lisasime tänasele kellaajale kuupäeva: " + curArtPubDate, 3)
    return curArtPubDate


def article_urls_range(articleUrls):
    """
    Esimesest edasi kuni objektide lõpuni
    """
    rss_print.print_debug(__file__, 'xpath parsimisel leitud artikleid: ' + str(len(articleUrls)), 2)
    return range(0, len(articleUrls))


def article_posts_range(articlePosts, maxArticlePostsCount):
    """
    Viimasest tagasi kuni piirarvu täitumiseni
    """
    rss_print.print_debug(__file__, 'xpath parsimisel leitud artikli poste: ' + str(len(articlePosts)), 2)
    return range(max(0, len(articlePosts) - maxArticlePostsCount), len(articlePosts))


def capitalize_first(inpString):
    return inpString[0:1].capitalize() + inpString[1:]


def del_article_dict_index(articleDataDict, k):
    rss_print.print_debug(__file__, "eemaldame mittesoovitud kande: '" + articleDataDict["titles"][k] + "'", 2)

    articleDataDict["authors"] = del_if_set(articleDataDict["authors"], k)
    articleDataDict["descriptions"] = del_if_set(articleDataDict["descriptions"], k)
    articleDataDict["images"] = del_if_set(articleDataDict["images"], k)
    articleDataDict["pubDates"] = del_if_set(articleDataDict["pubDates"], k)
    articleDataDict["titles"] = del_if_set(articleDataDict["titles"], k)
    articleDataDict["urls"] = del_if_set(articleDataDict["urls"], k)

    return articleDataDict


def del_if_set(inpList, inpIndex):
    indexHumanreadable = inpIndex + 1
    if len(inpList) >= indexHumanreadable:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(len(inpList)) + ", eemaldasime listi elemendi nr: " + str(indexHumanreadable), 4)
        del inpList[inpIndex]
    else:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(len(inpList)) + ", ei eemaldand listi elementi nr: " + str(indexHumanreadable), 4)
    return inpList


def domain_url(domain, articleUrl):
    """
    Ühendab domeenid URLidega
    """
    articleUrl = domain.rstrip('/') + '/' + articleUrl.lstrip('./').lstrip('/')
    rss_print.print_debug(__file__, "pärast domeeni lisamist lingile: " + str(articleUrl), 4)
    return articleUrl


def domain_urls(domain, urls):
    """
    Ühendab domeenid URLidega
    """
    domainUrls = []
    for curUrl in urls:
        domainUrls.append(domain_url(domain, curUrl))
    return domainUrls


def elemtree_to_string(elemTree):
    curString = str(lxml.html.tostring(elemTree))
    curString = fix_string_spaces(curString)
    return curString


def fix_broken_utf8_as_encoding(brokenBytearray, encoding='iso8859_15'):  # 'iso8859_4', 'iso8859_15'
    """
    Imiteerime vigast 'UTF-8' sisu -> 'enkooding' formaati konverteerimist ja asendame nii leitud vigased sümbolid algsete sümbolitega
    http://i18nqa.com/debug/UTF8-debug.html
    """

    rss_print.print_debug(__file__, "parandame ebaõnnestunud 'UTF-8' as 'iso8859_15' kodeeringu", 0)

    curBytearray = brokenBytearray.decode(encoding, 'ignore')

    for curInt in range(0x80, 383):  # ž on 382 ja selle juures lõpetame
        byteUnicode = str(chr(curInt))

        try:
            byteUTF8inEncode = byteUnicode.encode('utf-8').decode(encoding)
        except Exception:
            rss_print.print_debug(__file__, "i=" + str(hex(curInt)) + "\tbyteUnicode: " + str(byteUnicode) + "\t<-\tbyteUTF8inEncode: pole sümbolit", 4)
            continue

        rss_print.print_debug(__file__, "i=" + str(hex(curInt)) + "\tbyteUnicode: " + str(byteUnicode) + "\t<-\tbyteUTF8inEncode: " + str(byteUTF8inEncode), 4)
        curBytearray = curBytearray.replace(byteUTF8inEncode, byteUnicode)
    curBytearray = curBytearray.replace('â', '"')
    curBytearray = curBytearray.replace('â', '"')
    curBytearray = curBytearray.replace('â', '–')
    curBytearray = curBytearray.replace('â', '"')

    return curBytearray.encode('utf-8')


def fix_drunk_post(drunkPostString):
    drunkPostString = drunkPostString.strip()
    drunkPostString = drunkPostString.replace("   ", " ")
    drunkPostString = drunkPostString.replace("  ", " ")
    drunkPostString = drunkPostString + ". "

    drunkPostString = drunkPostString.replace(":<", ": <").replace(": </", ":</")

    drunkPostString = drunkPostString.replace(" :", ": ").replace(":  ", ": ")
    drunkPostString = drunkPostString.replace(": D ", " ").replace(":D ", " ").replace(": D.", ".").replace(":D.", ".")
    drunkPostString = drunkPostString.replace(": )", "").replace(":)", "").replace(": ).", ".").replace(":).", ".")
    drunkPostString = drunkPostString.replace(": (", "").replace(":(", "").replace(": (.", ".").replace(":(.", ".")
    drunkPostString = drunkPostString.replace(": -D", "").replace(":-D", "").replace(": -D.", ".").replace(":-D.", ".")
    drunkPostString = drunkPostString.replace(": -)", "").replace(":-)", "").replace(": -).", ".").replace(":-).", ".")
    drunkPostString = drunkPostString.replace(": -(", "").replace(":-(", "").replace(": -(.", ".").replace(":-(.", ".")
    drunkPostString = drunkPostString.replace("; )", "").replace(";)", "").replace("; ).", ".").replace(";).", ".")
    drunkPostString = drunkPostString.replace("; -)", "").replace(";-)", "").replace("; -).", ".").replace(";-).", ".")

    drunkPostString = drunkPostString.replace("  ", " ")
    drunkPostString = re.sub(r"\.(?=[A-Z])", ". ", drunkPostString)  # fix: space after dot
    drunkPostString = drunkPostString.replace(" ... ", "...").replace(" ..", ". ").replace(". .", ". ").replace(" .", ". ")
    drunkPostString = drunkPostString.replace(".... ", "... ").replace(".. ", ". ").replace(".. ", "... ")  # to remove '.. ', and keep '... '
    drunkPostString = drunkPostString.replace('" .', '".').replace(' ".', '".')
    drunkPostString = drunkPostString.replace(".<", ". <").replace(". </", ".</")
    drunkPostString = drunkPostString.replace(".(", ". (")

    drunkPostString = drunkPostString.replace("  ", " ")
    drunkPostString = re.sub(r"\,(?=[a-zA-Z])", ", ", drunkPostString)  # fix: space after commas
    drunkPostString = drunkPostString.replace(",.", ", ")
    drunkPostString = drunkPostString.replace(",(", ", (")
    drunkPostString = drunkPostString.replace(" ,", ", ")

    drunkPostString = drunkPostString.replace("?. ", "? ").replace("? .", "?")
    drunkPostString = drunkPostString.replace(" ?", "? ")

    drunkPostString = drunkPostString.replace("!. ", "! ").replace("! .", "!")
    drunkPostString = drunkPostString.replace(" !", "! ")

    drunkPostString = drunkPostString.replace(" ( ", " (").replace("( ", " (")

    drunkPostString = drunkPostString.replace(")))", ")").replace("))", ")")
    drunkPostString = drunkPostString.replace(" ) ", ") ").replace(" )", ") ")
    drunkPostString = drunkPostString.replace(" ).", "). ").replace(") . ", "). ")
    drunkPostString = drunkPostString.replace(" ),", "), ").replace(") ,", "), ")

    drunkPostString = drunkPostString.replace("- ", " - ").replace("- - ", "-- ").replace("-- ", " -- ").replace(" - ", " -- ")

    drunkPostString = drunkPostString.replace("  ", " ")
    return drunkPostString


def fix_string_spaces(inpString):
    """
    Tagastab formaatimata teksti
    Sisend utf-8 kujul inpString
    """

    inpString = inpString.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    inpString = " ".join(inpString.split())

    return inpString


def format_tags(htmlString, searchTagStart, searchTagEnd, addedTagStart, addedTagEnd):
    if (htmlString.find(searchTagStart) < 0):
        rss_print.print_debug(__file__, "ei leidnud searchTagStart = '" + str(searchTagStart) + "', lõpetame", 4)
        return htmlString

    rss_print.print_debug(__file__, "leidsime searchTagStart = '" + str(searchTagStart) + "', tegeleme", 4)

    rss_print.print_debug(__file__, "\n inpHtmlString = \n'" + str(htmlString) + "'\n", 2)

    # splitime lõpu järgi
    inpStringSplittedByEnd = htmlString.split(searchTagEnd)
    countEnds = len(inpStringSplittedByEnd)

    if countEnds == 0:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + ", lõpetame", 0)
        return htmlString
    if countEnds == 1:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + "", 1)
    else:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + "", 4)

    iAlreadyChanged = -1
    for i in range(0, countEnds - 1):
        rss_print.print_debug(__file__, "[" + str(i) + "] inpStringSplittedByEnd[" + str(i) + "] = \n'" + str(inpStringSplittedByEnd[i]) + "'", 2)

        if (i == iAlreadyChanged):
            rss_print.print_debug(__file__, "[" + str(i) + "] juba muudetud väärtus: inpStringSplittedByEnd[" + str(i) + "] = \n'" + str(inpStringSplittedByEnd[i]) + "', liigume järgmisele", 2)
            continue
        if (inpStringSplittedByEnd[i].find(searchTagStart) < 0):
            rss_print.print_debug(__file__, "[" + str(i) + "] ei leidnud searchTagStart = '" + str(searchTagStart) + "', liigume järgmisele", 4)
            continue
        else:
            rss_print.print_debug(__file__, "[" + str(i) + "] leidsime searchTagStart = '" + str(searchTagStart) + "', tegeleme", 4)

        splitByEndStringSplitByStart = inpStringSplittedByEnd[i].split(searchTagStart)

        countEndStarts = len(splitByEndStringSplitByStart)  # siin esimene ei loe

        if countEndStarts - 1 > 1:
            rss_print.print_debug(__file__, "[" + str(i) + "] algus(" + searchTagStart + ") leide: " + str(countEndStarts - 1) + "", 0)
        elif countEndStarts - 1 == 1:
            rss_print.print_debug(__file__, "[" + str(i) + "] algus(" + searchTagStart + ") leide: " + str(countEndStarts - 1) + "", 1)
        else:
            rss_print.print_debug(__file__, "[" + str(i) + "] algus(" + searchTagStart + ") leide: " + str(countEndStarts - 1) + "", 0)

        # paneme alguse paika
        splitByEndStringSplitByStart[1] = addedTagStart + splitByEndStringSplitByStart[1]

        # genereerime otsinguks lõputägist nn algusttagi
        searchStartTagFromSearchEnd = searchTagEnd.replace("</", "<").replace(">", "") + " "

        for j in range(0, countEndStarts):
            curNr = "[" + str(i) + "][" + str(j) + "/" + str(countEndStarts - 1) + "]"
            rss_print.print_debug(__file__, curNr + " asume uurima: splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 4)

            if (splitByEndStringSplitByStart[j] == ""):
                continue
            elif (splitByEndStringSplitByStart[j].find(searchStartTagFromSearchEnd) < 0):
                # sisus div-e juurde ei tuld, saame rahus lõpetada
                rss_print.print_debug(__file__, curNr + " ei leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 2)
                splitByEndStringSplitByStart[j] = splitByEndStringSplitByStart[j] + addedTagEnd
                rss_print.print_debug(__file__, curNr + " lõppu lisatud: splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 2)
                break
            elif (j == countEndStarts - 1):
                # sisus tuli div-e juurde, aga oleme lõpus, peame liikuma edasi
                rss_print.print_debug(__file__, curNr + " viimasest leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 2)
                for k in range(i + 1, countEnds - 1):
                    rss_print.print_debug(__file__, curNr + "[" + str(k) + "] liigume sammu edasi", 4)
                    inpStringSplittedByEnd[k] = addedTagEnd + inpStringSplittedByEnd[k]
                    rss_print.print_debug(__file__, curNr + "[" + str(k) + "] muudetud järgmine inpStringSplittedByEnd[" + str(k) + "] = '" + str(inpStringSplittedByEnd[k]) + "'", 1)
                    iAlreadyChanged = k
                    break
            else:
                rss_print.print_debug(__file__, curNr + " leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 0)
                # peame liikuma kindlasti edasi

        # paneme tükid kokku tagasi
        inpStringSplittedByEnd[i] = searchTagStart.join(splitByEndStringSplitByStart)
        rss_print.print_debug(__file__, "[" + str(i) + "] kokkupandud inpStringSplittedByEnd[" + str(i) + "] = '" + str(inpStringSplittedByEnd[i]) + "'", 2)

    htmlString = searchTagEnd.join(inpStringSplittedByEnd)
    rss_print.print_debug(__file__, "\n outHtmlString = \n'" + str(htmlString) + "'\n", 2)
    return htmlString


def get_article_data(session, domain, articleUrl, mainPage=False):
    if (articleUrl.find('http', 0, 4) == -1):
        rss_print.print_debug(__file__, "lingist ei leitud http-d: " + str(articleUrl), 3)
        articleUrl = domain_url(domain, articleUrl)
    return rss_makereq.get_article_data(session, articleUrl, mainPage)


def html_to_string(htmlNode, pageTreeEcoding='utf-8'):
    if isinstance(htmlNode, str):
        rss_print.print_debug(__file__, "sisend on juba string: htmlNode = " + str(htmlNode), 2)
        return htmlNode

    rss_print.print_debug(__file__, "type(htmlNode) = " + str(type(htmlNode)), 2)
    rss_print.print_debug(__file__, "htmlNode = " + str(htmlNode), 2)
    stringAsBytes = html.tostring(htmlNode, encoding=pageTreeEcoding)
    string = str(stringAsBytes)
    return string


def lstrip_string(inpString, stripString):
    if (inpString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: inpString = '" + str(inpString) + "'", 3)
        return inpString
    if (stripString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: stripString = '" + str(stripString) + "'", 0)
        return inpString

    lenStripString = len(stripString)
    while (inpString.find(stripString) == 0):
        rss_print.print_debug(__file__, "eemaldasime algusest stringi: '" + str(stripString) + "'", 4)
        inpString = inpString[lenStripString:]
    return inpString


def rstrip_string(inpString, stripString):
    if (inpString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: inpString = '" + str(inpString) + "'", 3)
        return inpString
    if (stripString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: stripString = '" + str(stripString) + "'", 0)
        return inpString

    lenStripString = len(stripString)
    while (inpString.find(stripString) == len(inpString) - lenStripString):
        rss_print.print_debug(__file__, "eemaldasime lõpust stringi '" + str(stripString) + "': " + str(inpString), 4)
        inpString = inpString[:len(inpString) - lenStripString]
    return inpString


def max_article_bodies(articleUrl):
    """
    Hashi genereerimine lehekülje URList
    """
    return hashlib.md5(articleUrl.encode('utf-8')).hexdigest()


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
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    rss_print.print_debug(__file__, "rawDateTimeText = '" + rawDateTimeText + "'", 4)
    rss_print.print_debug(__file__, "rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 4)
    datetimeFloat = raw_to_float(rawDateTimeText, rawDateTimeSyntax)
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
    if (curDateTimeText == ""):
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


def remove_weekday_strings(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    # est
    rawDateTimeText = rawDateTimeText.replace('esmaspäev', "").replace('teisipäev', "").replace('kolmapäev', "")
    rawDateTimeText = rawDateTimeText.replace('neljapäev', "").replace('reede', "").replace('laupäev', "").replace('pühapäev', "")
    return rawDateTimeText


def replace_string_with_timeformat(inpString, stringToReplace, dateTimeformat, offSetDays=0):
    if (inpString.find(stringToReplace) >= 0):
        inpString = inpString.replace(stringToReplace, str((datetime.now() + timedelta(days=offSetDays)).strftime(dateTimeformat)))
        rss_print.print_debug(__file__, "asendasime stringis sõna ajaga: '" + stringToReplace + "' -> " + inpString, 3)
    return inpString


def months_to_int(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
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


def stringify_index_children(sourceList, index, pageTreeEcoding='utf-8'):
    if (index >= len(sourceList)):
        rss_print.print_debug(__file__, "sisendilistis pole indeksit " + str(index) + ", tagastame tühja sisu", 0)
        return ""

    node = sourceList[index]
    nodeChilds = stringify_children(node, pageTreeEcoding='utf-8')

    return nodeChilds


def stringify_children(node, pageTreeEcoding='utf-8'):
    """
    Given a LXML tag, return contents as a string
    >>> html = "<p><strong>Sample sentence</strong> with tags.</p>"
    >>> node = lxml.html.fragment_fromstring(html)
    >>> extract_html_content(node)
    "<strong>Sample sentence</strong> with tags."
    From: https://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml/32468202#32468202
    """

    if node is None:
        rss_print.print_debug(__file__, "pole otsitavat parentit (node is None), tagastame tühja sisu", 1)
        return ""

    if (len(node) == 0):
        rss_print.print_debug(__file__, "osakontroll1: (if (len(node) == 0):)", 4)
        if not getattr(node, 'text', None):
            rss_print.print_debug(__file__, "osakontroll2: (if not getattr(node, 'text', None):)", 4)
            rss_print.print_debug(__file__, "pole otsitavat parentit (node-s puudub attr. 'text'), tagastame tühja sisu", 3)
            return ""
    if isinstance(node, str):
        rss_print.print_debug(__file__, "stringify_children() sisend on string, ehk juba töödeldud?, katkestame töötluse", 0)
        return node

    node.attrib.clear()
    tagLen = len(node.tag)  # len(b) = 1
    tagOpening = tagLen + 2  # <b> = 1 + 2
    tagClosing = -(tagLen + 2 + 1)  # <b/> = 1 + 3
    retString = html.tostring(node, encoding=pageTreeEcoding)[tagOpening:tagClosing]

    try:
        retString = retString.decode(pageTreeEcoding)
    except Exception as e:
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        retString = fix_broken_utf8_as_encoding(retString, 'iso8859_15')
        retString = retString.decode(pageTreeEcoding)

    retString = to_plaintext(retString)
    return retString


def to_plaintext(rawText):
    """
    Tagastab formaatimata teksti
    Sisend utf-8 kujul rawText
    """

    retString = rawText.replace('<strong>', '<br><strong>').replace('</td>', '</td> ').replace('</p>', '</p> ')
    retString = fix_string_spaces(retString)

    return retString


def url_to_hash(articleUrl):
    """
    Hashi genereerimine lehekülje URList
    """

    return hashlib.md5(articleUrl.encode('utf-8')).hexdigest()


def xpath_path_validator(xpathString, parent=False):
    if xpathString.find("/html") != 0 and xpathString.find("//") != 0:
        rss_print.print_debug(__file__, "xpath-i stringi algus mittekorrektne: " + xpathString, 0)
    if xpathString.find('""') > -1:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '\"\"', asendame '\"'-ga: " + xpathString, 0)
        xpathString = xpathString.replace('""', '"')
    if xpathString.find("///") > -1:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '///', asendame '//'-ga: " + xpathString, 0)
        xpathString = xpathString.replace("///", "//")
    if re.search(r"\[([a-zA-Z])\w+", xpathString):
        rss_print.print_debug(__file__, "xpath-i stringis on kummaline '[*', äkki on '@' puudu: " + xpathString, 0)
    if xpathString[1:].find("//") > 0:
        rss_print.print_debug(__file__, "xpath-i stringis on '//', tasuks optimeerida: " + xpathString, 3)
    if re.search(r"\[([0-9]*)\]", xpathString):
        rss_print.print_debug(__file__, "xpath-i stringis on asukoht '[nr', tasuks vältida: " + xpathString, 3)

    xpathStringEnd = xpathString.split("/")[-1]

    if parent is False:
        logLevelHas = 5
        logLevelNot = 0
    else:
        logLevelHas = 0
        logLevelNot = 5

    if xpathStringEnd.find("text()") == 0:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on 'text()': " + xpathString, logLevelHas)
    elif xpathStringEnd.find("@") == 0:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on '@': " + xpathString, logLevelHas)
    elif xpathStringEnd.find("node()") == 0:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on 'node()': " + xpathString, logLevelHas)
    else:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is puudub ('node()','text()','@'): " + xpathString, logLevelNot)

    return xpathString


def xpath_to_list(pageTree, xpathString, parent=False):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid
    """

    xpathString = xpath_path_validator(xpathString, parent)

    elements = pageTree.xpath(xpathString)

    if (parent is True):
        rss_print.print_debug(__file__, "laseme nimekirja läbi funktsiooni stringify_index_children", 3)
    for i in range(len(elements)):
        # enne hangimine, kui vaja
        if (parent is True):
            elements[i] = stringify_index_children(elements, i)
        # ja siis ühine stripp
        elements[i] = elements[i].strip()

    if not elements:
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtuste pikkus: " + str(len(elements)), 0)
    elif len(elements) > 1:
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtuste pikkus: " + str(len(elements)), 4)
    else:
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtuste pikkus: " + str(len(elements)), 1)

    rss_print.print_debug(__file__, "tagastame xpathi: '" + xpathString + "' väärtused: elements = " + str(elements), 3)

    return elements


def xpath_to_list_devel(pageTree, xpathString, parent=False):
    rss_print.print_debug(__file__, "xpath-i stringi pärimine funktsiooni 'xpath_to_list_devel' kaudu: " + xpathString, 0)

    xpathString = xpath_path_validator(xpathString, parent)

    while(True):
        elements = pageTree.xpath(xpathString)

        if elements:
            rss_print.print_debug(__file__, "xpath-i " + str(len(elements)) + " stringi leitud: " + xpathString, 0)
            rss_print.print_debug(__file__, "elements: " + str(elements), 3)
            return elements

        rss_print.print_debug(__file__, "xpath-i stringile ei leitud vasteid: " + xpathString, 0)

        if len(xpathString.split("/")) <= 3:
            rss_print.print_debug(__file__, "xpath-i ei anna enam lühendada: " + xpathString, 0)
            return elements

        rss_print.print_debug(__file__, "xpath-i lühendamine algusest: " + xpathString, 0)
        xpathString = "//" + "/".join(xpathString.replace("/html", "//").split("/")[3:])


def xpath_to_single(pageTree, xpathString, parent=False, combine=False):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objekt
    """

    xpathString = xpath_path_validator(xpathString, parent)

    element = next(iter(pageTree.xpath(xpathString) or [""]), None)

    if (parent is True):
        element = stringify_children(element)

    if not element:
        rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtuse pikkus: " + str(len(element)), 2)
        element = ""
    elif len(element) > 1:
        rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtuse pikkus: " + str(len(element)), 4)

    rss_print.print_debug(__file__, "tagastame xpathi: '" + xpathString + "' väärtuse: '" + str(element) + "'", 3)
    return element
