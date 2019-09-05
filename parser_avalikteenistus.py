#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[1]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[5]/div[1]/a/@href')

    articleDescParents = parsers_common.xpath_to_list(pageTree, '//table[@class="views-table cols-5"]/tbody/tr', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtDescChilds = parsers_common.stringify_index_children(articleDescParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

    # remove unwanted content
    k = 0
    while (k < len(articleDataDict["urls"])):
        rss_print.print_debug(__file__, "kontrollime kannet" + str(k + 1) + "/" + str(len(articleDataDict["urls"])) + ": " + articleDataDict["titles"][k], 3)
        if ('Tartu' in articleDataDict["descriptions"][k]) or ('Türi' in articleDataDict["descriptions"][k]):
            k += 1
        else:
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)

    return articleDataDict
