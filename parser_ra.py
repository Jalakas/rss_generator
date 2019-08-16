#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//li[@class="b-posts__list-item"]/p[@class="b-posts__list-item-summary"]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/@href')

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        # timeformat magic from "03.01" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i].strip()
        curArtPubDate = parsers_common.add_to_time_string(curArtPubDate, "%Y.")
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%Y.%d.%m")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (getArticleBodies is True) and (i < maxArticleCount):
            # load article into tree
            articleTree = parsers_common.getArticleData(domain, articleDataDict["urls"][i], False)

            # description
            curArtDescChilds = parsers_common.xpath_parent_to_single(articleTree, '//div[@class="b-article"]')
            articleDataDict["descriptions"].append(curArtDescChilds)

    return articleDataDict
