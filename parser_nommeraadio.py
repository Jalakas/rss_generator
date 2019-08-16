#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/a/@href')
    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/div[@class="audiolist_item_label"]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/div[@class="audiolist_item_label"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_header"]/a/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//div[@class="audiolist_item"]/div[@class="audiolist_item_bottom"]/div[@class="audioitem_item_desc"]')  # as a parent

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        # description
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

        # timeformat magic from "15.12.2017 - L" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = curArtPubDate.split('-')[0]
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
        articleDataDict["pubDates"][i] = curArtPubDate

    return articleDataDict
