#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

        # timeformat magic from "29.08.19" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%y")
        articleDataDict["pubDates"][i] = curArtPubDate

    # remove unwanted content
    k = 0
    while (k < len(articleDataDict["urls"])):
        rss_print.print_debug(__file__, "kontrollime kannet(" + str(k + 1) + "/" + str(len(articleDataDict["urls"])) + "): " + articleDataDict["titles"][k], 2)
        if ('Tartu' not in articleDataDict["descriptions"][k]):
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
        else:
            k += 1

    return articleDataDict
