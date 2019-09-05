#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/p[@class="img"]/a/img/@src')
    articleDataDict["pubDates"] = []
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

    # remove unwanted content
    k = 0
    while (k < len(articleDataDict["urls"])):
        rss_print.print_debug(__file__, "kontrollime kannet" + str(k + 1) + "/" + str(len(articleDataDict["urls"])) + ": " + articleDataDict["titles"][k], 3)
        if (
                articleDataDict["titles"][k].find("Aktuaalne kaamera") >= 0 or
                articleDataDict["titles"][k].find("Ringvaade") >= 0
        ):
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
        else:
            k += 1

    return articleDataDict
