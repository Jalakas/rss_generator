#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, session):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/p[@class="img"]/a/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/@href')

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]', parent=True)

    # remove unwanted content
    k = 0
    while (k < len(articleDataDict["urls"])):
        rss_print.print_debug(__file__, "kontrollime kannet" + str(k + 1) + "/" + str(len(articleDataDict["urls"])) + ": " + articleDataDict["titles"][k], 3)
        if (
                articleDataDict["titles"][k].find("Aktuaalne kaamera") >= 0 or
                articleDataDict["titles"][k].find("NOVA") >= 0 or
                articleDataDict["titles"][k].find("Ringvaade") >= 0
        ):
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
        else:
            k += 1

    return articleDataDict
