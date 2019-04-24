#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HTML-i hankimine
"""

from lxml import html
import os
import requests

import rss_config
import rss_print


def getArticleData(articleURL, mainPage=False):
    """
    Artikli lehe pärimine
    """

    cacheArticleURL = articleURL.replace('/', '|')
    cacheDomainFolder = articleURL.split('/')[2]

    osPath = os.path.dirname(os.path.abspath(__file__))
    osCacheFolder = osPath + '/' + 'article_cache'
    osCacheFolderDomain = osCacheFolder + '/' + cacheDomainFolder
    osCacheFolderDomainArticle = osCacheFolderDomain + '/' + cacheArticleURL

    if mainPage is True:
        # põhilehekülg tuleb alati alla laadida Internetist
        rss_print.print_debug(__file__, "teeme internetipäringu lehele: " + articleURL)
        htmlPageString = makeReq(articleURL)
    else:
        try:
            # proovime kõigepealt hankida kettalt
            with open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
                htmlPageString = cacheReadFile.read()
                rss_print.print_debug(__file__, "lugesime kettalt: " + osCacheFolderDomainArticle, 2)
        except Exception:
            rss_print.print_debug(__file__, "ei õnnestunud kettalt lugeda: " + osCacheFolderDomainArticle)

            # kui kettalt ei leidnud, hangime veebist
            rss_print.print_debug(__file__, "teeme internetipäringu lehele: " + articleURL)
            htmlPageString = makeReq(articleURL)

            # ja salvestame alati kettale
            if not os.path.exists(osCacheFolder):
                os.makedirs(osCacheFolder)
            if not os.path.exists(osCacheFolderDomain):
                os.makedirs(osCacheFolderDomain)
            with open(osCacheFolderDomainArticle, 'wb') as cacheWriteFile:
                cacheWriteFile.write(htmlPageString)

    # kontrollime kodeeringut
    try:
        htmlPageString.decode("utf-8")
    except Exception:
        rss_print.print_debug("makereg: parandame ebaõnnestunud 'UTF-8' as 'iso8859_15' kodeeringu veebilehel: " + articleURL)
        htmlPageString = fixBrokenUTF8asEncoding(htmlPageString, 'iso8859_15')

    # eemaldame ::before, sest see teeb tõenäoliselt XML extractori katki
    # htmlPageString = htmlPageString.replace("::before", "")

    # teeme html puu
    articleTree = html.fromstring(htmlPageString)
    return articleTree


def fixBrokenUTF8asEncoding(brokenBytearray, encoding='iso8859_15'):  # 'iso8859_4', 'iso8859_15'
    """
    Imiteerime vigast 'UTF-8' sisu -> 'enkooding' formaati konverteerimist ja asendame nii leitud vigased sümbolid algsete sümbolitega
    http://i18nqa.com/debug/UTF8-debug.html
    """

    curBytearray = brokenBytearray.decode(encoding, 'ignore')

    for curInt in range(0x80, 383):  # ž on 382 ja selle juures lõpetame
        byteUnicode = str(chr(curInt))

        try:
            byteUTF8inEncode = byteUnicode.encode('utf-8').decode(encoding)
        except Exception:
            # rss_print.print_debug("i=" + str(hex(curInt)) + "\tbyteUnicode: " + str(byteUnicode) + "\t<-\tbyteUTF8inEncode: pole sümbolit")
            continue

        # rss_print.print_debug("i=" + str(hex(curInt)) + "\tbyteUnicode: " + str(byteUnicode) + "\t<-\tbyteUTF8inEncode: " + str(byteUTF8inEncode))
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

    session = requests.session()

    req = session.get(link, headers=rss_config.headers)
    return req.content
