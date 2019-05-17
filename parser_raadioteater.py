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
    articleImages = []
    articlePubDates = []
    articleTitles = []
    articleUrls = parsers_common.xpath(pageTree, '//div[@id="body1"]/h1/a/@href')

    articleTitlesParents = parsers_common.xpath(pageTree, '//div[@id="body1"]/h1/a')  # as a parent

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # titles
        curArtTitlesChilds = parsers_common.stringify_children(articleTitlesParents[i])
        articleTitles.append(curArtTitlesChilds)

        if (getArticleBodies is True):
            # load article into tree
            articleTree = parsers_common.getArticleData(domain, articleUrls[i], False)

            # description
            curArtDescParent = parsers_common.treeExtract(articleTree, '//div[@id="body1"]/div[@class="uudis_sisu"]')  # as a parent
            curArtDescriptionsChilds = parsers_common.stringify_children(curArtDescParent)
            articleDescriptions.append(curArtDescriptionsChilds)

            # media
            curArtPubImage = parsers_common.treeExtract(articleTree, '//div[@id="body1"]/div[@class="listeningItem"]/p/audio/source/@src') or "/"
            articleImages.append(curArtPubImage)

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
