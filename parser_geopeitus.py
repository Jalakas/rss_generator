#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Geopeituse "Tartu" RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr')

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        # description
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

        # timeformat magic from "12.12.2017" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
        articleDataDict["pubDates"][i] = curArtPubDate

    # remove unwanted content
    k = 0
    while (k < min(len(articleDataDict["urls"]), maxArticleCount)):
        rss_print.print_debug(__file__, "kontrollime kannet: " + str(k + 1) + ", kokku: " + str(len(articleDataDict["urls"])), 4)
        if ('Tartu' not in articleDataDict["descriptions"][k]):
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
        else:
            k += 1

    return articleDataDict
