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
    articleImages = parsers_common.xpath(pageTree, '//div[@class="product"]//div[@class="table-cell image-cell"]/img/@src')
    articlePubDates = []
    articleTitles = parsers_common.xpath(pageTree, '//div[@class="product"]//div[@class="table-cell description-cell"]/h2/text()')
    articleUrls = parsers_common.xpath(pageTree, '//div[@class="product"]//div[@class="table-cell description-cell"]/a/@href')

    articleDescriptionsParents = parsers_common.xpath(pageTree, '//div[@class="product"]//div[@class="table-cell description-cell"]')  # as a parent

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # description
        curArtDescriptionsChilds = parsers_common.stringify_children(articleDescriptionsParents[i])
        articleDescriptions.append(curArtDescriptionsChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
