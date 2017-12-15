#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Kuma RSS-voo sisendite parsimine
"""

import hashlib
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
    return None


def getNewsList(newshtml, domain):
    """
    Peameetod kõigi uudiste nimekirja loomiseks
    """
    tree = html.fromstring(newshtml)

    articleBodys = []
    articleDescriptions = tree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-excerpt"]/p/text()')
    articleIds = []
    articleImages = tree.xpath('//div[@class="news-list-media"]/img/@src')
    articleImages = [domain + elem for elem in articleImages]
    articlePubDates = []
    articleTitles = tree.xpath('//div[@class="news-list-item-wrapper"]/h3/a/text()')
    articleUrls = tree.xpath('//div[@class="news-list-item-wrapper"]/h3/a/@href')
    articleUrls = [domain + elem for elem in articleUrls]

    articlePubDay = tree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/text()[1]')
    articlePubMonth = tree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/span[@class="month"]/text()')
    articlePubYear = tree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/text()[2]')

    for i in range(0, len(articleUrls) - 1):
        articleUrl = articleUrls[i]

        # generate unical id from link
        articleIds.append(hashlib.md5(articleUrl.encode('utf-8')).hexdigest())

        if (get_article_bodies is True):
            articleTree = parsers_common.getArticleData(articleUrl)

            # todo(BROKEN)
            buf = extractArticleBody(articleTree)
            print(buf)
            articleBodys.append(buf)

            artPubDateRaw = parsers_common.treeExtract(articleTree, '//div[@class="news-single-timedata"]/text()')

            # timeformat magic from "13 dets  17" to datetime()
            artPubDateRaw = artPubDateRaw.strip().replace('  ', ' ')
            artPubDateRaw = artPubDateRaw.replace('jaan', '01').replace('veeb', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
            artPubDateRaw = artPubDateRaw.replace('juuli', '07').replace('aug', '08').replace('sept', '09').replace('okt', '10').replace('nov', '11').replace('dets', '12')
            articlePubDates.append(datetime.datetime.fromtimestamp(mktime(time.strptime(artPubDateRaw, "%d %m %y"))))  # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        else:
            if i < len(articlePubYear) and (int(articlePubYear[i].strip()) > 2016):
                curYear = articlePubYear[i].strip()
            artPubDateRaw = articlePubDay[i].strip() + " " + articlePubMonth[i].strip() + " " + curYear
            artPubDateRaw = datetime.datetime.fromtimestamp(mktime(time.strptime(artPubDateRaw, "%d %m %Y")))
            articlePubDates.append(artPubDateRaw)

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articleIds": articleIds,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
