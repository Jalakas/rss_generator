#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Lõunaeestlane RSS-voo sisendite parsimine
"""

from lxml import html
import parsers_common


def getArticleListsFromHtml(htmlPage, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """
    tree = html.fromstring(htmlPage)

    articleDescriptions = tree.xpath('//div[@class="midColPost"]/p/text()')
    articleIds = []
    articleImages = tree.xpath('//div[@class="midColPost"]/a/img/@src')
    articlePubDates = []
    articleTitles = tree.xpath('//div[@class="midColPost"]/h2/a/@title')
    articleUrls = tree.xpath('//div[@class="midColPost"]/h2/a/@href')

    articlePubDatesRaw = tree.xpath('//div[@class="midColPost"]/span/text()[1]')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl.split("?p=")[1])

        # timeformat magic from "15. detsember 2017 / " to datetime()
        curArtPubDate = articlePubDatesRaw[i]
        curArtPubDate = parsers_common.longMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d. %m %Y /")
        articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
