#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod kõigi objektide nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = []
    articleTitles = []
    articleUrls = pageTree.xpath('//div[@id="body1"]/h1/a/@href')

    articleTitlesParents = pageTree.xpath('//div[@id="body1"]/h1/a')  # as a parent
    articleDescriptionsParents = pageTree.xpath('//div/div[@class="uudis_sisu"]/p')  # as a parent

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # get unique id from articleUrl
        articleIds.append(articleUrls[i].rstrip("/"))

        # description
        curArtDescriptionsChilds = parsers_common.stringify_children(articleDescriptionsParents[i])
        articleDescriptions.append(curArtDescriptionsChilds)

        # titles
        curArtTitlesChilds = parsers_common.stringify_children(articleTitlesParents[i])
        articleTitles.append(curArtTitlesChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
