#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    BNS RSS-voo sisendite parsimine
"""

import hashlib
from lxml import html
import time
import datetime
from time import mktime

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

    articleDescriptions = tree.xpath('//div[@class="js-newsline-container"]/div/a/text()')
    articleIds = []
    articleImages = []
    articlePubDates = []
    articleTitles = tree.xpath('//div[@class="js-newsline-container"]/div/a/text()')
    articleUrls = tree.xpath('//div[@class="js-newsline-container"]/div/a/@href')

    artPubDateRaw = tree.xpath('//div[@class="js-newsline-container"]/span[1]/text()')
    articleDescriptionsTag = tree.xpath('//div[@class="js-newsline-container"]/div/span[1]/text()')

    for i in range(0, len(articleUrls) - 1):
        articleUrl = articleUrls[i]

        # generate unical id from link
        articleIds.append(hashlib.md5(articleUrl.encode('utf-8')).hexdigest())

        articleDescriptions[i] = articleDescriptionsTag[i] + ". " + articleDescriptions[i]

        # timeformat magic from "14 dets  2017 11:34" to datetime()
        curArtPubDatesRaw = artPubDateRaw[i]
        curArtPubDatesRaw = curArtPubDatesRaw.replace('jaan', '01').replace('veeb', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
        curArtPubDatesRaw = curArtPubDatesRaw.replace('juuli', '07').replace('aug', '08').replace('sept', '09').replace('okt', '10').replace('nov', '11').replace('dets', '12').replace('  ', ' ')
        curArtPubDates = datetime.datetime.fromtimestamp(mktime(time.strptime(curArtPubDatesRaw, "%d %m %Y %H:%M")))  # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        articlePubDates.append(curArtPubDates)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
