#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HTML-i hankimine
"""

import os
import re
import requests
from lxml import html

import parsers_common
import rss_config
import rss_disk
import rss_print

CACHE_MAIN_ARTICLE_BODIES = False


def get_article_data(articleUrl, mainPage=False):
    """
    Artikli lehe pärimine
    """

    cacheArticleUrl = articleUrl.replace('/', '|')
    cacheDomainFolder = articleUrl.split('/')[2]

    osPath = os.path.dirname(os.path.abspath(__file__))
    osCacheFolder = osPath + '/' + 'article_cache'
    osCacheFolderDomain = osCacheFolder + '/' + cacheDomainFolder
    osCacheFolderDomainArticle = osCacheFolderDomain + '/' + cacheArticleUrl

    if mainPage is True and CACHE_MAIN_ARTICLE_BODIES is False:
        # põhilehekülg tuleb alati alla laadida Internetist, kui me pole devel režiimis
        htmlPageBytes = make_request(articleUrl)

        # salvestame alati kettale
        rss_disk.write_file_to_cache_folder(osCacheFolder, osCacheFolderDomain, osCacheFolderDomainArticle, htmlPageBytes)
    else:
        rss_print.print_debug(__file__, "hangitav leht: " + articleUrl, 1)

        # proovime kõigepealt hankida kettalt
        htmlPageBytes = rss_disk.read_file_from_cache(osCacheFolderDomainArticle)

        if htmlPageBytes != "":
            rss_print.print_debug(__file__, "lugesime kettalt: " + osCacheFolderDomainArticle, 2)
        else:
            rss_print.print_debug(__file__, "ei õnnestunud kettalt lugeda: " + osCacheFolderDomainArticle, 1)

            # teeme internetipäringu
            htmlPageBytes = make_request(articleUrl)

            # salvestame alati kettale
            rss_disk.write_file_to_cache_folder(osCacheFolder, osCacheFolderDomain, osCacheFolderDomainArticle, htmlPageBytes)

    # teeme html puu
    try:
        articleTree = html.fromstring(htmlPageBytes)
    except Exception as e:
        rss_print.print_debug(__file__, "ei õnnestunud luua html objekti leheküljest: " + articleUrl, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

    return articleTree


def make_request(articleUrl):
    """
    Päringu teostamine HTML-i allalaadimiseks
    """
    # teeme päringu
    try:
        rss_print.print_debug(__file__, "teeme internetipäringu lehele: " + articleUrl, 0)
        session = requests.session()
        htmlPage = session.get(articleUrl, headers=rss_config.HEADERS, timeout=10)
        htmlPageBytes = htmlPage.content
    except Exception as e:
        rss_print.print_debug(__file__, "päring ebaõnnestus, tagastame tühja vastuse", 0)
        rss_print.print_debug(__file__, "exception = " + str(e), 0)
        htmlPageBytes = bytes("", encoding='utf-8')

    # kontrollime kodeeringut
    try:
        htmlPageString = htmlPageBytes.decode("utf-8")
    except Exception as e:
        rss_print.print_debug(__file__, "exception = " + str(e), 0)
        htmlPageString = parsers_common.fix_broken_utf8_as_encoding(htmlPageBytes, 'iso8859_15')

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
