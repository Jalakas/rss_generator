#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Rahvusarhiivi RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleImages = []
    articlePubDates = parsers_common.xpath(pageTree, '//li[@class="b-posts__list-item"]/p[@class="b-posts__list-item-summary"]/text()')
    articleTitles = parsers_common.xpath(pageTree, '//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/text()')
    articleUrls = parsers_common.xpath(pageTree, '//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/@href')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # timeformat magic from "03.01" to datetime()
        curArtPubDate = articlePubDates[i].strip()
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m")
        articlePubDates[i] = curArtPubDate

        if (getArticleBodies is True):
            # load article into tree
            articleTree = parsers_common.getArticleData(domain, articleUrls[i], False)

            # description
            curArtDescParent = parsers_common.treeExtract(articleTree, '//div[@class="b-article"]')  # as a parent
            curArtDescriptionsChilds = parsers_common.stringify_children(curArtDescParent)
            articleDescriptions.append(curArtDescriptionsChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
