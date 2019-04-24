#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Erinevate parserid ja funktsioonid
"""

import datetime
import hashlib
import time
import lxml
from lxml import html
from time import mktime

import rss_makereq
import rss_print


def domainUrl(domain, url):
    """
    Ühendab domeenid URLidega
    """
    return domain.rstrip('/') + '/' + url.lstrip('./').lstrip('/')


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


def getArticleData(articleURL, mainPage=False):
    return rss_makereq.getArticleData(articleURL, mainPage)


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
    ret = datetime.datetime.fromtimestamp(mktime(time_tuple))
    rss_print.print_debug(__file__, "curDateTimeRet = '" + str(ret) + "'", 4)
    return ret


def shortMonthsToNumber(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    rawDateTimeText = rawDateTimeText.replace('jaan', '01').replace('veebr', '02').replace('veeb', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
    rawDateTimeText = rawDateTimeText.replace('juuli', '07').replace('aug', '08').replace('sept', '09').replace('okt', '10').replace('nov', '11').replace('dets', '12')
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
    rawText = rawText.strip().rstrip('</').rstrip('<')

    return rawText


def treeExtract(tree, xpathValue):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid
    """
    return next(
        iter(
            tree.xpath(xpathValue) or []),
        None)


def urlToHash(articleURL):
    """
    Hashi genereerimine lehekülje URList
    """
    return hashlib.md5(articleURL.encode('utf-8')).hexdigest()
