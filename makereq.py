#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HTML-i hankimine
"""

import requests
from lxml import html


def getArticleData(articleURL):
    """
    Artikli lehe pärimine
    """
    aricleDataHtml = makeReq(articleURL)

    if (aricleDataHtml.decode("iso8859_15", 'ignore').find(u"\xc3")):
        print("makereg: parandame ebaõnnestunud 'UTF-8' as 'iso8859_15' veebilehe kodeeringu")
        aricleDataHtml = fixBrokenUTF8asEncoding(aricleDataHtml, 'iso8859_15')

    treeArt = html.fromstring(aricleDataHtml)
    return treeArt


def fixBrokenUTF8asEncoding(brokenBytearray, encoding='iso8859_15'):  # 'iso8859_4', 'iso8859_15'
    """
    Imiteerime vigast 'UTF-8' sisu -> 'enkooding' formaati konverteerimist ja asendame nii leitud vigased sümbolid algsete sümbolitega
    http://i18nqa.com/debug/UTF8-debug.html
    """

    curBytearray = brokenBytearray.decode(encoding, 'ignore')

    for curInt in range(0x80, 383):  # ž on 382
        byteUnicode = str(chr(curInt))

        try:
            byteUTF8inEncode = byteUnicode.encode('utf-8').decode(encoding)
        except Exception:
            #  print("i=" + str(hex(curInt)) + "\tbyteUnicode: " + str(byteUnicode) + "\t<-\tbyteUTF8inEncode: pole sümbolit")
            continue

        #  print("i=" + str(hex(curInt)) + "\tbyteUnicode: " + str(byteUnicode) + "\t<-\tbyteUTF8inEncode: " + str(byteUTF8inEncode))
        curBytearray = curBytearray.replace(byteUTF8inEncode, byteUnicode)
    curBytearray = curBytearray.replace('â', '"')
    curBytearray = curBytearray.replace('â', '"')
    curBytearray = curBytearray.replace('â', '–')
    curBytearray = curBytearray.replace('â', '"')

    return curBytearray.encode('utf-8')


def makeReq(link):
    """
    Päringu teostamine HTML-i allalaadimiseks
    """
    headers = {
        'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
        'Accept-Encoding': 'gzip, deflate, compress'}
    session = requests.session()
    req = session.get(link, headers=headers)
    return req.content
