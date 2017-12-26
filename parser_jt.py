#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    JT RSS-voo sisendite parsimine
"""

import makereq
import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = []
    articleTitles = pageTree.xpath('//ul[@class="list search-items-list"]/li/span/a/text()')
    articleUrls = pageTree.xpath('//ul[@class="list search-items-list"]/li/span/a/@href')

    articlePubDatesRaw = pageTree.xpath('//ul[@class="list search-items-list"]/li/div/span[2]/text()')

    get_article_bodies = True

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from ArticleUrl
        articleIds.append(articleUrl.split('/')[-2])

        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articleTree = makereq.getArticleData(articleUrl)

            # description
            curArtDescParent1 = parsers_common.treeExtract(articleTree, '//main/article/div[@class="flex flex--align-items-stretch"]//section')  # as a parent
            curArtDescParent2 = parsers_common.treeExtract(articleTree, '//main/div[@class="wrap"]/div[@class="flex flex--align-items-stretch"]//section')  # as a parent
            curArtDescChilds1 = parsers_common.stringify_children(curArtDescParent1)
            curArtDescChilds2 = parsers_common.stringify_children(curArtDescParent2)
            articleDescriptions.append(curArtDescChilds1 + ' ' + curArtDescChilds2)

            # image
            curArtImg = parsers_common.treeExtract(articleTree, '//main/article/div[@class="flex flex--align-items-stretch"]//figure/img[1]/@src') or "//"
            curArtImg = "http:" + curArtImg
            articleImages.append(curArtImg)

            # timeformat magic from "24. detsember 2017 17:51" to datetime()
            curArtPubDate = articlePubDatesRaw[i]
            curArtPubDate = parsers_common.longMonthsToNumber(curArtPubDate)
            curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d. %m %Y %H:%M")
            articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
