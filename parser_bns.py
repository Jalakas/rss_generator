#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    BNS RSS-voo sisendite parsimine
"""

from lxml import html
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

    articleDescriptions = tree.xpath('//div[@class="js-newsline-container"]/div/a/text()')
    articleIds = []
    articleImages = []
    articlePubDates = []
    articleTitles = tree.xpath('//div[@class="js-newsline-container"]/div/a/text()')
    articleUrls = tree.xpath('//div[@class="js-newsline-container"]/div/a/@href')

    articlePubDatesRaw = tree.xpath('//div[@class="js-newsline-container"]/span[1]/text()')
    articleDescriptionsTag = tree.xpath('//div[@class="js-newsline-container"]/div/span[1]/text()')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # generate unical id from link
        articleIds.append(articleUrl.split('/')[-2])

        articleDescriptions[i] = articleDescriptionsTag[i] + ". " + articleDescriptions[i]

        # timeformat magic from "14 dets  2017 11:34" to datetime()
        curArtPubDate = articlePubDatesRaw[i]
        curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d %m %Y %H:%M")
        articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
