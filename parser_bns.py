#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod saidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleImages = []
    articlePubDates = parsers_common.xpath(pageTree, '//div[@class="js-newsline-container"]/span[1]/text()')
    articleTitles = parsers_common.xpath(pageTree, '//div[@class="js-newsline-container"]/div/a/text()')
    articleUrls = parsers_common.xpath(pageTree, '//div[@class="js-newsline-container"]/div/a/@href')

    articleDescriptionsTag = parsers_common.xpath(pageTree, '//div[@class="js-newsline-container"]/div/span[1]/text()')
    articleDescriptionsRaw = parsers_common.xpath(pageTree, '//div[@class="js-newsline-container"]/div/a/text()')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # timeformat magic from "14 dets  2017 11:34" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d %m %Y %H:%M")
        articlePubDates[i] = curArtPubDate

        if (getArticleBodies is True):
            # load article into tree
            articleTree = parsers_common.getArticleData(domain, articleUrls[i], False)

            # description
            curArtDescParent = parsers_common.treeExtract(articleTree, '//div[@class="news-preview"]/div')  # as a parent
            curArtDescriptionsChilds = parsers_common.stringify_children(curArtDescParent)
            articleDescriptions.append(curArtDescriptionsChilds)
        else:
            # description
            articleDescriptions.append(articleDescriptionsTag[i] + "<br>" + articleDescriptionsRaw[i])

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
