#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Nõmmeraadio RSS-voo sisendite parsimine
"""

from lxml import html
import parsers_common

get_article_bodies = False


def getNewsList(newshtml, domain):
    """
    Peameetod kõigi uudiste nimekirja loomiseks
    """
    tree = html.fromstring(newshtml)

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = []
    articleTitles = tree.xpath('//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/div[@class="audiolist_item_label"]/text()')
    articleUrls = tree.xpath('//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/a/@href')

    articleDescriptionsRaw = tree.xpath('//div[@class="audiolist_item"]/div[@class="audiolist_item_bottom"]/div[@class="audioitem_item_desc"]')  # as a parent
    articlePubDatesRaw = tree.xpath('//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/div[@class="audiolist_item_label"]/text()')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # generate unical id from link
        articleIds.append(parsers_common.urlToHash(articleUrl))

        curArtDesc = parsers_common.stringify_children(articleDescriptionsRaw[i])
        articleDescriptions.append(curArtDesc.decode("utf-8"))

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
