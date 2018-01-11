#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Lõunaeestlane RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = pageTree.xpath('//div[@class="midColPost"]/p/text()')
    articleIds = []
    articleImages = pageTree.xpath('//div[@class="midColPost"]/a/img/@src')
    articlePubDates = pageTree.xpath('//div[@class="midColPost"]/span/text()[1]')
    articleTitles = pageTree.xpath('//div[@class="midColPost"]/h2/a/@title')
    articleUrls = pageTree.xpath('//div[@class="midColPost"]/h2/a/@href')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl.split("?p=")[1])

        # timeformat magic from "15. detsember 2017 / " to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.longMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d. %m %Y /")
        articlePubDates[i] = curArtPubDate

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
