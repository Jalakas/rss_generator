#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    BNS RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = pageTree.xpath('//div[@class="js-newsline-container"]/div/a/text()')
    articleIds = []
    articleImages = []
    articlePubDates = []
    articleTitles = pageTree.xpath('//div[@class="js-newsline-container"]/div/a/text()')
    articleUrls = pageTree.xpath('//div[@class="js-newsline-container"]/div/a/@href')

    articlePubDatesRaw = pageTree.xpath('//div[@class="js-newsline-container"]/span[1]/text()')
    articleDescriptionsTag = pageTree.xpath('//div[@class="js-newsline-container"]/div/span[1]/text()')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unical id from articleUrl
        articleIds.append(articleUrl.split('/')[-2])

        # description
        articleDescriptions[i] = articleDescriptionsTag[i] + "<br>" + articleDescriptions[i]

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
