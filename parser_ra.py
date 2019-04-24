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
    articleIds = []
    articleImages = []
    articlePubDates = pageTree.xpath('//li[@class="b-posts__list-item"]/p[@class="b-posts__list-item-summary"]/text()')
    articleTitles = pageTree.xpath('//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/text()')
    articleUrls = pageTree.xpath('//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/@href')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # get unique id from articleUrl
        articleIds.append(articleUrls[i].split('-')[-1])

        # timeformat magic from "03.01" to datetime()
        curArtPubDate = articlePubDates[i].strip()
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m")
        articlePubDates[i] = curArtPubDate

        if (getArticleBodies is True):
            # load article into tree
            articleTree = parsers_common.getArticleData(articleUrls[i])

            # description
            curArtDescParent = parsers_common.treeExtract(articleTree, '//div[@class="b-article"]')  # as a parent
            curArtDescriptionsChilds = parsers_common.stringify_children(curArtDescParent)
            articleDescriptions.append(curArtDescriptionsChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
