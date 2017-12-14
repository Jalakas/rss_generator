#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Tartu Ekspressi RSS-voo sisendite parsimine
"""

from lxml import html
import time
import datetime
from time import mktime
import parsers_common


get_article_bodies = False


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
        articleTree = parsers_common.getArticleData(elem)

        articleIds.append(
            elem[elem.index('&id=') + 4:elem.index('&', elem.index('&id=') + 4)])

        articleHeaders.append(parsers_common.treeExtract(articleTree, '//div[@class="full_width"]/p[1]/strong/text()'))

        articleImages.append(domain + parsers_common.treeExtract(articleTree, '//div[@class="full_width"]/a/img[@class="thumb"]/@src'))

        articlePubDateRaw = parsers_common.treeExtract(articleTree, '//div[@class="full_width"]/p[*]/i/b[2]/text()')

        # timeformat magic from "13/12/2017 22:24:59" to to datetime()
        articlePubDate.append(datetime.datetime.fromtimestamp(mktime(time.strptime(articlePubDateRaw, "%d/%m/%Y %H:%M:%S"))))  # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

        if (get_article_bodies is True):
            articleBodys.append(extractArticleBody(articleTree))

    return {"articleIds": articleIds,
            "articleUrls": newsUrls,
            "articleTitles": headLines,
            "articleHeaders": articleHeaders,
            "articleImages": articleImages,
            "articleBodys": articleBodys,
            "articlePubDate": articlePubDate,
            }
