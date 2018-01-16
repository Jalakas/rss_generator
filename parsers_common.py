#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Erinevate parserid ja funktsioonid
"""

import datetime
import hashlib
import time
from lxml import html
from time import mktime


def domainUrls(domain, urls):
    """
    Ühendab domeenid URLidega
    """
    domainUrls = []
    for i in range(0, len(urls)):
        domainUrls.append(domain.rstrip('/') + '/' + urls[i].lstrip('./').lstrip('/'))
    return domainUrls


def rawToDatetime(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """
    time_tuple_list = list(time.strptime(rawDateTimeText, rawDateTimeSyntax))
    if time_tuple_list[0] == 1900:
        if time_tuple_list[1] > int(time.strftime('%m')):
            print('parsers_common: muudame puuduva aasta eelmiseks aastaks')
            time_tuple_list[0] = int(time.strftime('%Y')) - 1
        else:
            print('parsers_common: muudame puuduva aasta praeguseks aastaks')
            time_tuple_list[0] = int(time.strftime('%Y'))
    time_tuple = tuple(time_tuple_list)
    ret = datetime.datetime.fromtimestamp(mktime(time_tuple))
    return ret


def longMonthsToNumber(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    rawDateTimeText = rawDateTimeText.replace('jaanuar', '01').replace('veebruar', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
    rawDateTimeText = rawDateTimeText.replace('juuli', '07').replace('august', '08').replace('september', '09').replace('oktoober', '10').replace('november', '11').replace('detsember', '12')
    return rawDateTimeText


def shortMonthsToNumber(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    rawDateTimeText = rawDateTimeText.replace('jaan', '01').replace('veeb', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
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
    ret = ret.decode(pageTreeEcoding)
    ret = toPlaintext(ret)
    return ret


def toPlaintext(rawText):
    """
    Tagastab formaatimata teksti
    Sisend utf-8 kujul rawText
    """
    return rawText.replace('<strong>', '<br><strong>').replace('</td>', ' </td>').replace('</p>', ' </p>').\
        replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ').strip().rstrip('</').rstrip('<')


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
