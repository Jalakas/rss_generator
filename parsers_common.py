#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Erinevate parserid ja funktsioonid
"""

import datetime
import hashlib
import time
import lxml
from email import utils
from lxml import html
from time import mktime

import rss_makereq
import rss_print


def del_if_set(inpList, inpIndex):
    indexHumanreadable = inpIndex + 1
    if len(inpList) >= indexHumanreadable:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(len(inpList)) + ", eemaldasime listi elemendi nr: " + str(indexHumanreadable), 4)
        del inpList[inpIndex]
    else:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(len(inpList)) + ", ei eemaldand listi elementi nr: " + str(indexHumanreadable), 4)
    return inpList


def domainUrl(domain, articleUrl):
    """
    Ühendab domeenid URLidega
    """
    articleUrl = domain.rstrip('/') + '/' + articleUrl.lstrip('./').lstrip('/')
    rss_print.print_debug(__file__, "pärast domeeni lisamist lingile: " + str(articleUrl), 4)
    return articleUrl


def domainUrls(domain, urls):
    """
    Ühendab domeenid URLidega
    """
    domainUrls = []
    for i in range(0, len(urls)):
        domainUrls.append(domainUrl(domain, urls[i]))
    return domainUrls


def elemtreeToString(elemTree):
    return toPlaintext(str(lxml.html.tostring(elemTree)))


def fixDrunkPost(drunkPostString):
    drunkPostString = drunkPostString.replace(" : -)", ". ").replace(":-)", ". ").replace(" :)", ". ").replace(":) ", "")
    drunkPostString = drunkPostString.replace(" : D", ". ").replace(": D ", ". ").replace(" :D", ". ")
    drunkPostString = drunkPostString.replace(" :", ": ")
    drunkPostString = drunkPostString.replace(".<", ". <").replace(":<", ": <")
    drunkPostString = drunkPostString.replace(" ..", ". ").replace(". .", ". ").replace(" .", ". ")
    drunkPostString = drunkPostString.replace(",.", ", ").replace(" ,", ", ")
    drunkPostString = drunkPostString.replace("?. ", "? ").replace(" ?", "? ")
    drunkPostString = drunkPostString.replace(" !", "! ")
    drunkPostString = drunkPostString.replace(" ( ", " (")
    drunkPostString = drunkPostString.replace(" ) ", ") ")
    drunkPostString = drunkPostString.replace("  ", " ")
    return drunkPostString


def getArticleData(domain, articleUrl, mainPage=False):
    if (articleUrl.find('http', 0, 4) == -1):
        rss_print.print_debug(__file__, "lingist ei leitud http-d: " + str(articleUrl), 2)
        articleUrl = domainUrl(domain, articleUrl)
    return rss_makereq.getArticleData(articleUrl, mainPage)


def longMonthsToNumber(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    rawDateTimeText = rawDateTimeText.replace('jaanuar', '01').replace('veebruar', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
    rawDateTimeText = rawDateTimeText.replace('juuli', '07').replace('august', '08').replace('september', '09').replace('oktoober', '10').replace('november', '11').replace('detsember', '12')
    return rawDateTimeText


def lstrip_string(inpString, stripString):
    while (inpString.find(stripString) == 0):
        inpString = inpString[len(stripString):]
    return inpString


def maxArticleCount(articleUrl):
    """
    Hashi genereerimine lehekülje URList
    """
    return hashlib.md5(articleUrl.encode('utf-8')).hexdigest()


def rawToDatetime(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    curDateTimeText = rawDateTimeText.strip()
    rss_print.print_debug(__file__, "curDateTimeText = '" + curDateTimeText + "'", 4)

    time_tuple_list = list(time.strptime(curDateTimeText, rawDateTimeSyntax))
    if time_tuple_list[0] == 1900:
        if time_tuple_list[1] > int(time.strftime('%m')):
            rss_print.print_debug(__file__, "muudame puuduva aasta eelmiseks aastaks", 0)
            time_tuple_list[0] = int(time.strftime('%Y')) - 1
        else:
            rss_print.print_debug(__file__, "muudame puuduva aasta praeguseks aastaks", 0)
            time_tuple_list[0] = int(time.strftime('%Y'))
    time_tuple = tuple(time_tuple_list)
    art_PubDate_datetime = datetime.datetime.fromtimestamp(mktime(time_tuple))
    art_PubDate_tuple = art_PubDate_datetime.timetuple()
    art_PubDate_timestamp = time.mktime(art_PubDate_tuple)
    art_PubDate_RFC2822 = utils.formatdate(art_PubDate_timestamp, True, True)
    rss_print.print_debug(__file__, "curDateTimeRet = '" + str(art_PubDate_RFC2822) + "'", 4)
    return art_PubDate_RFC2822


def shortMonthsToNumber(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    # est
    rawDateTimeText = rawDateTimeText.replace('jaan', '01').replace('veebr', '02').replace('veeb', '02').replace('märts', '03').replace('mär', '03')
    rawDateTimeText = rawDateTimeText.replace('aprill', '04').replace('mai', '05').replace('juuni', '06').replace('juun', '06')
    rawDateTimeText = rawDateTimeText.replace('juuli', '07').replace('aug', '08').replace('sept', '09')
    rawDateTimeText = rawDateTimeText.replace('okt', '10').replace('nov', '11').replace('dets', '12')
    # eng
    rawDateTimeText = rawDateTimeText.replace('jan', '01').replace('feb', '02').replace('mar', '03').replace('apr', '04').replace('may', '05').replace('jun', '06')
    rawDateTimeText = rawDateTimeText.replace('jul', '07').replace('aug', '08').replace('sep', '09').replace('oct', '10').replace('nov', '11').replace('dec', '12')
    return rawDateTimeText


def stringify_children(node, pageTreeEcoding='utf-8'):
    """
    Given a LXML tag, return contents as a string
    >>> html = "<p><strong>Sample sentence</strong> with tags.</p>"
    >>> node = lxml.html.fragment_fromstring(html)
    >>> extract_html_content(node)
    "<strong>Sample sentence</strong> with tags."
    From: https://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml/32468202#32468202
    """
    if node is None or (len(node) == 0 and not getattr(node, 'text', None)):
        return ""
    node.attrib.clear()
    opening_tag = len(node.tag) + 2
    closing_tag = -(len(node.tag) + 4)
    ret = html.tostring(node, encoding=pageTreeEcoding)[opening_tag:closing_tag]
    try:
        ret = ret.decode(pageTreeEcoding)
    except Exception:
        rss_print.print_debug(__file__, "parandame ebaõnnestunud 'UTF-8' kodeeringu")
        ret = rss_makereq.fixBrokenUTF8asEncoding(ret, 'iso8859_15')
        ret = ret.decode(pageTreeEcoding)
    ret = toPlaintext(ret)
    return ret


def toPlaintext(rawText):
    """
    Tagastab formaatimata teksti
    Sisend utf-8 kujul rawText
    """

    rawText = rawText.replace('<strong>', '<br><strong>').replace('</td>', '</td> ').replace('</p>', '</p> ')
    rawText = rawText.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    rawText = " ".join(rawText.split())
    rawText = rawText.strip()

    return rawText


def treeExtract(pageTree, xpathString):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid
    """

    return next(
        iter(
            xpath(pageTree, xpathString) or []),
        None)


def urlToHash(articleUrl):
    """
    Hashi genereerimine lehekülje URList
    """

    return hashlib.md5(articleUrl.encode('utf-8')).hexdigest()


def xpath(pageTree, xpathString):
    if xpathString.find("///") > 0:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '///', asendame '//'-ga: " + xpathString, 0)
        xpathString = xpathString.replace("///", "//")
    if xpathString.find("//") > 0:
        rss_print.print_debug(__file__, "xpath-i stringis on '//', tasuks optimeerida: " + xpathString, 0)
    if xpathString.find("//") != 0 and xpathString.find("/html") != 0:
        rss_print.print_debug(__file__, "xpath-i stringi algus mittekorrektne: " + xpathString, 0)
    if xpathString.find("text()") < 1 and xpathString.find("@") < 1:
        rss_print.print_debug(__file__, "xpath-i stringis pole 'text()' ega '@' otsingut: " + xpathString, 0)
    return pageTree.xpath(xpathString)


def xpath_devel(pageTree, xpathString):
    rss_print.print_debug(__file__, "xpath-i stringi pärimine funktsiooni 'xpath_devel' kaudu: " + xpathString, 0)

    while(True):
        found = pageTree.xpath(xpathString)
        if len(found) > 0:
            rss_print.print_debug(__file__, "xpath-i " + str(len(found)) + " stringi leitud: " + xpathString, 0)
            return found
        else:
            rss_print.print_debug(__file__, "xpath-i stringile ei leitud vasteid: " + xpathString, 0)
            if len(xpathString.split("/")) < 3:
                rss_print.print_debug(__file__, "xpath-i ei anna lühendada: " + xpathString, 0)
                return found
            else:
                rss_print.print_debug(__file__, "xpath-i lühendamine algusest: " + xpathString, 0)
                xpathString = "//" + "/".join(xpathString.replace("/html", "//").split("/")[3:])
