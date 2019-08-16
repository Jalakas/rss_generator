#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HTML-i hankimine
"""

from lxml import html
import gzip
import os
import re
import requests

import rss_config
import rss_print

cacheMainArticleBodies = False


def getArticleData(articleUrl, mainPage=False):
    """
    Artikli lehe pärimine
    """

    cacheArticleUrl = articleUrl.replace('/', '|')
    cacheDomainFolder = articleUrl.split('/')[2]

    osPath = os.path.dirname(os.path.abspath(__file__))
    osCacheFolder = osPath + '/' + 'article_cache'
    osCacheFolderDomain = osCacheFolder + '/' + cacheDomainFolder
    osCacheFolderDomainArticle = osCacheFolderDomain + '/' + cacheArticleUrl

    if mainPage is True and cacheMainArticleBodies is False:
        # põhilehekülg tuleb alati alla laadida Internetist, kui me pole devel režiimis
        htmlPageBytes = makeReq(articleUrl)

        # salvestame alati kettale
        writeFileToCacheFolder(osCacheFolder, osCacheFolderDomain, osCacheFolderDomainArticle, htmlPageBytes)
    else:
        rss_print.print_debug(__file__, "hangitav leht: " + articleUrl, 1)

        # proovime kõigepealt hankida kettalt
        htmlPageBytes = readFileFromCache(osCacheFolderDomainArticle)

        if htmlPageBytes != "":
            rss_print.print_debug(__file__, "lugesime kettalt: " + osCacheFolderDomainArticle, 2)
        else:
            rss_print.print_debug(__file__, "ei õnnestunud kettalt lugeda: " + osCacheFolderDomainArticle, 1)

            # teeme internetipäringu
            htmlPageBytes = makeReq(articleUrl)

            # salvestame alati kettale
            writeFileToCacheFolder(osCacheFolder, osCacheFolderDomain, osCacheFolderDomainArticle, htmlPageBytes)

    # teeme html puu
    try:
        articleTree = html.fromstring(htmlPageBytes)
    except Exception as e:
        rss_print.print_debug(__file__, "ei õnnestunud luua html objekti leheküljest: " + articleUrl, 0)
        rss_print.print_debug(__file__, "exception = " + str(e), 1)

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
            rss_print.print_debug(__file__, "i=" + str(hex(curInt)) + "\tbyteUnicode: " + str(byteUnicode) + "\t<-\tbyteUTF8inEncode: pole sümbolit", 4)
            continue

        rss_print.print_debug(__file__, "i=" + str(hex(curInt)) + "\tbyteUnicode: " + str(byteUnicode) + "\t<-\tbyteUTF8inEncode: " + str(byteUTF8inEncode), 4)
        curBytearray = curBytearray.replace(byteUTF8inEncode, byteUnicode)
    curBytearray = curBytearray.replace('â', '"')
    curBytearray = curBytearray.replace('â', '"')
    curBytearray = curBytearray.replace('â', '–')
    curBytearray = curBytearray.replace('â', '"')

    return curBytearray.encode('utf-8')


def makeReq(articleUrl):
    """
    Päringu teostamine HTML-i allalaadimiseks
    """

    rss_print.print_debug(__file__, "teeme internetipäringu lehele: " + articleUrl, 0)

    session = requests.session()
    htmlPage = session.get(articleUrl, headers=rss_config.headers)
    htmlPageBytes = htmlPage.content

    # kontrollime kodeeringut
    try:
        htmlPageString = htmlPageBytes.decode("utf-8")
    except Exception:
        rss_print.print_debug(__file__, "parandame ebaõnnestunud 'UTF-8' as 'iso8859_15' kodeeringu veebilehel: " + articleUrl, 0)
        htmlPageString = fixBrokenUTF8asEncoding(htmlPageBytes, 'iso8859_15')

    # remove style
    htmlPageString = re.sub(r"<style[\s\S]*?<\/style>", "", htmlPageString)

    # remove scripts
    htmlPageString = re.sub(r"<script[\s\S]*?<\/script>", "", htmlPageString)

    # remove comments
    htmlPageString = re.sub(r"<!--[\s\S]*?-->", "", htmlPageString)

    # eemaldame html-i vahelise whitespace-i
    htmlPageString = re.sub(r"\s\s+(?=<)", "", htmlPageString)

    htmlPageBytes = bytes(htmlPageString, encoding='utf-8')
    return htmlPageBytes


def readFileFromCache(osCacheFolderDomainArticle):
    try:
        with gzip.open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
            htmlPageBytes = cacheReadFile.read()
            return htmlPageBytes
    except Exception as e:
        rss_print.print_debug(__file__, "exception = " + str(e), 2)
        # pakitud faili ei leidnud, proovime tavalist
        try:
            with open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
                htmlPageBytes = cacheReadFile.read()
                return htmlPageBytes
        except Exception as e:
            rss_print.print_debug(__file__, "exception = " + str(e), 3)
            return ""


def recursively_empty(e):
    if e.text:
        return False
    return all((recursively_empty(c) for c in e.iterchildren()))


def writeFileAsGzip(filePath, htmlPageBytes):
    with gzip.open(filePath, 'wb') as cacheWriteFile:
        rss_print.print_debug(__file__, "salvestame kettale faili: " + filePath, 3)
        cacheWriteFile.write(htmlPageBytes)
        cacheWriteFile.close()
        uid = os.environ.get('SUDO_UID')
        gid = os.environ.get('SUDO_GID')
        if uid is not None:
            os.chown(filePath, int(uid), int(gid))


def writeFileToCacheFolder(osCacheFolder, osCacheFolderDomain, osCacheFolderDomainArticle, htmlPageBytes):
    if not os.path.exists(osCacheFolder):
        rss_print.print_debug(__file__, "loome puuduva kausta: " + osCacheFolder, 0)
        os.makedirs(osCacheFolder)
    if not os.path.exists(osCacheFolderDomain):
        rss_print.print_debug(__file__, "loome puuduva kausta: " + osCacheFolderDomain, 0)
        os.makedirs(osCacheFolderDomain)
    try:
        writeFileAsGzip(osCacheFolderDomainArticle, htmlPageBytes)
        rss_print.print_debug(__file__, "fail õnnestus kettale salvestada: " + osCacheFolderDomainArticle, 2)
    except Exception as e:
        rss_print.print_debug(__file__, "faili ei õnnestunud kettale salvestada: " + osCacheFolderDomainArticle, 0)
        rss_print.print_debug(__file__, "exception = " + str(e), 1)
