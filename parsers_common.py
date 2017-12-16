#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Parserid ja funktsioonid erinevate lehtedega kasutamiseks
"""

import datetime
import hashlib
import makereq
import time
from lxml import html
from time import mktime


def extractArticleBody(tree):
    """
    Artikli tervikteksti saamiseks
    """
    return None


def getArticleData(articleURL):
    """
    Artikli lehe pärimine
    """
    aricleDataHtml = makereq.makeReq(articleURL)
    treeArt = html.fromstring(aricleDataHtml)
    return treeArt


def rawToDatetime(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 / "
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y / "
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    ret = datetime.datetime.fromtimestamp(mktime(time.strptime(rawDateTimeText, rawDateTimeSyntax)))
    return ret


def shortMonthsToNumber(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    rawDateTimeText = rawDateTimeText.replace('jaan', '01').replace('veeb', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
    rawDateTimeText = rawDateTimeText.replace('juuli', '07').replace('aug', '08').replace('sept', '09').replace('okt', '10').replace('nov', '11').replace('dets', '12')
    return rawDateTimeText


def longMonthsToNumber(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    rawDateTimeText = rawDateTimeText.replace('jaanuar', '01').replace('veebruar', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
    rawDateTimeText = rawDateTimeText.replace('juuli', '07').replace('august', '08').replace('september', '09').replace('oktoober', '10').replace('november', '11').replace('detsember', '12')
    return rawDateTimeText


def stringify_children(node):
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
    return html.tostring(node)[opening_tag:closing_tag]


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
