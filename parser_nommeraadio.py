#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod saidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleImages = parsers_common.xpath(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/a/@href')
    articlePubDates = parsers_common.xpath(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/div[@class="audiolist_item_label"]/text()')
    articleTitles = parsers_common.xpath(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/div[@class="audiolist_item_label"]/text()')
    articleUrls = parsers_common.xpath(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/a/@href')

    articleDescriptionsParents = parsers_common.xpath(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_bottom"]/div[@class="audioitem_item_desc"]')  # as a parent

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # description
        curArtDesc = parsers_common.stringify_children(articleDescriptionsParents[i])
        articleDescriptions.append(curArtDesc)

        try:
            # timeformat magic from "15.12.2017 - L" to datetime()
            curArtPubDate = articlePubDates[i] or '15.12.2017 - L'
            curArtPubDate = curArtPubDate.split('-')[0]
            curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
            curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
            articlePubDates[i] = curArtPubDate
        except Exception:
            rss_print.print_debug(__file__, "toores aeg puudub või on vigane")

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
