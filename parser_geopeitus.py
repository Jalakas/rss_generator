#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Geopeituse "Tartu" RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod Tartu aarete nimekirja loomiseks
    """

    articleDescriptions = []
    # articleImages = []
    articlePubDates = parsers_common.xpath(pageTree, '//div[@id="t-content"]/table[1]/tr/td[1]/text()')
    articleTitles = parsers_common.xpath(pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/text()')
    articleUrls = parsers_common.xpath(pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/@href')

    articleDescriptionsParents = parsers_common.xpath(pageTree, '//div[@id="t-content"]/table[1]/tr')  # as a parent

    retArticleDescriptions = []
    retArticleImages = []
    retArticlePubDates = []
    retArticleTitles = []
    retArticleUrls = []

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # description
        curArtDescParent = articleDescriptionsParents[i]
        curArtDescriptionsChilds = parsers_common.stringify_children(curArtDescParent)
        articleDescriptions.append(curArtDescriptionsChilds)

        # timeformat magic from "12.12.2017" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
        articlePubDates[i] = curArtPubDate

    # remove non "Tartu" location lines
    for i in range(0, min(len(articleUrls), maxArticleCount)):
        if ('Tartu' in articleDescriptions[i]):
            retArticleDescriptions.append(articleDescriptions[i])
            # retArticleImages.append(articleImages[i])
            retArticlePubDates.append(articlePubDates[i])
            retArticleTitles.append(articleTitles[i])
            retArticleUrls.append(articleUrls[i])

    return {"articleDescriptions": retArticleDescriptions,
            "articleImages": retArticleImages,
            "articlePubDates": retArticlePubDates,
            "articleTitles": retArticleTitles,
            "articleUrls": retArticleUrls,
           }
