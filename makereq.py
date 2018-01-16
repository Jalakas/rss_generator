#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HTML-i hankimine
"""

import requests
from lxml import html
import os


def getArticleData(articleURL, mainPage=False):
    """
    Artikli lehe pärimine
    """

    cacheFolder = articleURL.split('/')[2]
    cacheArcitcleURL = articleURL.replace('/', '|')

    if mainPage is True:
        aricleDataHtml = makeReq(articleURL)
    else:
        try:
            with open('article_cache/' + cacheFolder + '/' + cacheArcitcleURL, 'rb') as cacheReadFile:
                aricleDataHtml = cacheReadFile.read()
        except Exception:
            aricleDataHtml = makeReq(articleURL)

    try:
        aricleDataHtml.decode("utf-8")
    except Exception:
        print("makereg: parandame ebaõnnestunud 'UTF-8' as 'iso8859_15' kodeeringu veebilehel: " + articleURL)
        aricleDataHtml = fixBrokenUTF8asEncoding(aricleDataHtml, 'iso8859_15')

    # write article to cache
    if mainPage is False:
        if not os.path.exists('article_cache'):
            os.makedirs('article_cache')
        if not os.path.exists('article_cache/' + cacheFolder):
            os.makedirs('article_cache/' + cacheFolder)
        with open('article_cache/' + cacheFolder + '/' + cacheArcitcleURL, 'wb') as cacheWriteFile:
            cacheWriteFile.write(aricleDataHtml)

    articleTree = html.fromstring(aricleDataHtml)
    return articleTree


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
    print('makereg: teeme internetipäringu lehele: ' + link)
    req = session.get(link, headers=headers)
    return req.content
