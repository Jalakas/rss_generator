#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/p[@class="img"]/a/img/@src')
    articleDataDict["pubDates"] = []
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]')  # as a parent

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

    # remove unwanted content
    k = 0
    while (k < min(len(articleDataDict["urls"]), maxArticleCount)):
        rss_print.print_debug(__file__, "kontrollime kannet: " + str(k + 1) + ", kokku: " + str(len(articleDataDict["urls"])), 3)
        if (
            articleDataDict["titles"][k].find("Aktuaalne kaamera") >= 0 or
            articleDataDict["titles"][k].find("Ringvaade") >= 0
        ):
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
        else:
            k += 1

    return articleDataDict
