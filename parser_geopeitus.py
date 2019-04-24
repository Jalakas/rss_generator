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
    articleIds = []
    # articleImages = []
    articlePubDates = pageTree.xpath('//div[@id="t-content"]/table[1]/tr/td[1]/text()')
    articleTitles = pageTree.xpath('//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/text()')
    articleUrls = pageTree.xpath('//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/@href')

    articleDescriptionsParents = pageTree.xpath('//div[@id="t-content"]/table[1]/tr')  # as a parent

    retArticleDescriptions = []
    retArticleIds = []
    retArticleImages = []
    retArticlePubDates = []
    retArticleTitles = []
    retArticleUrls = []

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # get unique id from articleUrl
        articleIds.append(articleUrls[i].split('/')[-1])

        # description
        curArtDescParent = articleDescriptionsParents[i]
        curArtDescriptionsChilds = parsers_common.stringify_children(curArtDescParent)
        articleDescriptions.append(curArtDescriptionsChilds)

        # timeformat magic from "12.12.2017" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
        articlePubDates[i] = curArtPubDate

    # remove non "Tartu" ocation lines
    for i in range(0, min(len(articleUrls), maxArticleCount)):
        if ('Tartu' in articleDescriptions[i]):
            retArticleDescriptions.append(articleDescriptions[i])
            retArticleIds.append(articleIds[i])
            retArticlePubDates.append(articlePubDates[i])
            retArticleTitles.append(articleTitles[i])
            retArticleUrls.append(articleUrls[i])

    return {"articleDescriptions": retArticleDescriptions,
            "articleIds": retArticleIds,
            "articleImages": retArticleImages,
            "articlePubDates": retArticlePubDates,
            "articleTitles": retArticleTitles,
            "articleUrls": retArticleUrls,
           }
