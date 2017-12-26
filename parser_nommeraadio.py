#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Nõmmeraadio RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = []
    articleTitles = pageTree.xpath('//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/div[@class="audiolist_item_label"]/text()')
    articleUrls = pageTree.xpath('//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/a/@href')

    articleDescriptionsParents = pageTree.xpath('//div[@class="audiolist_item"]/div[@class="audiolist_item_bottom"]/div[@class="audioitem_item_desc"]')  # as a parent
    articlePubDatesRaw = pageTree.xpath('//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/div[@class="audiolist_item_label"]/text()')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # generate unique id from articleUrl
        articleIds.append(parsers_common.urlToHash(articleUrl))

        # descriptions
        curArtDesc = articleDescriptionsParents[i]
        curArtDesc = parsers_common.stringify_children(curArtDesc)
        articleDescriptions.append(curArtDesc)

        # timeformat magic from "15.12.2017 - L" to datetime()
        curArtPubDate = articlePubDatesRaw[i].split('-')[0]
        curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
        articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
