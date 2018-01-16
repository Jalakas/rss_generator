#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Rahvusarhiivi RSS-voo sisendite parsimine
"""

import makereq
import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = pageTree.xpath('//li[@class="b-posts__list-item"]/p[@class="b-posts__list-item-summary"]/text()')
    articleTitles = pageTree.xpath('//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/text()')
    articleUrls = pageTree.xpath('//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/@href')

    get_article_bodies = True

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl.split('-')[-1])

        # timeformat magic from "03.01" to datetime()
        curArtPubDate = articlePubDates[i].strip()
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m")
        articlePubDates[i] = curArtPubDate

        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articleTree = makereq.getArticleData(articleUrl)

            # description
            curArtDescParent = parsers_common.treeExtract(articleTree, '//div[@class="b-article"]')  # as a parent
            curArtDescChilds = parsers_common.stringify_children(curArtDescParent)
            articleDescriptions.append(curArtDescChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
