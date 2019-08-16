#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/figure/a/@data-original')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '///main/div/ul/li/figure/div/div/p/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/div/div/p/a/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/div[@class="offers-thumb__article-helper "]')  # as a parent

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        # description
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

    return articleDataDict
