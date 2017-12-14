#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Tartu Ekspressi RSS-voo loomiseks
"""

# from lxml import etree
from lxml import html
import makereq
import time
import datetime
from time import mktime


def getArticleData(articleURL):
    """
    Artikli lehe pärimine
    """
    aricleDataHtml = makereq.makeReq(articleURL)
    treeArt = html.fromstring(aricleDataHtml)
    return treeArt


def extractArticleHeader(tree):
    """
    Artikli päise saamiseks
    """
    return next(
        iter(
            tree.xpath('//div[@class="full_width"]/p[1]/strong/text()') or []),
        None)


def extractArticleImage(tree):
    """
    Artikli pildi aadressi saamiseks
    """
    return next(
        iter(
            tree.xpath('//div[@class="full_width"]/a/img[@class="thumb"]/@src') or []),
        None)


def extractArticlePubDate(tree):
    """
    Artikli ilmumisaja saamiseks
    """
    return next(
        iter(
            tree.xpath('//div[@class="full_width"]/p[*]/i/b[2]/text()') or []),
        None)


def extractArticleBody(tree):
    """
    Artikli tervikteksti saamiseks
    """
    body = tree.xpath('//div[@class="full_width"]/p')
    fulltext = []
    for elem in body:
        rawtext = elem.text_content()
        try:
            rawtext = rawtext[:rawtext.index('Tweet\n')]
        except ValueError:
            None
        fulltext.append(rawtext)
    return ''.join(fulltext)


def getNewsList(newshtml, domain):
    """
    Peameetod kõigi uudiste nimekirja loomiseks
    """
    tree = html.fromstring(newshtml)
    headLines = tree.xpath('//div[@class="forum"][2]/ul/li/a/text()')
    newsUrls = tree.xpath('//div[@class="forum"][2]/ul/li/a/@href')
    articleIds = []
    articleHeaders = []
    articleImages = []
    articleBodys = []
    articlePubDate = []
    newsUrls = [domain + elem for elem in newsUrls]

    for elem in newsUrls:
        articleIds.append(
            elem[elem.index('&id=') + 4:elem.index('&', elem.index('&id=') + 4)])
        articleTree = getArticleData(elem)

        articleHeaders.append(extractArticleHeader(articleTree))
        articleImages.append(domain + extractArticleImage(articleTree))
        articleBodys.append(extractArticleBody(articleTree))

        # timeformat magic from "13/12/2017 22:24:59" to to datetime()
        articlePubDateRaw = extractArticlePubDate(articleTree)
        articlePubDate.append(datetime.datetime.fromtimestamp(mktime(time.strptime(articlePubDateRaw, "%d/%m/%Y %H:%M:%S"))))  # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

    return {"articleIds": articleIds,
            "articleUrls": newsUrls,
            "articleTitles": headLines,
            "articleHeaders": articleHeaders,
            "articleImages": articleImages,
            "articleBodys": articleBodys,
            "articlePubDate": articlePubDate,
            }
