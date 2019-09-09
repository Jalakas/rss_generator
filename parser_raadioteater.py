#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, session):

    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@id="body1"]/h1/a/@href')

    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@id="body1"]/h1/a', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            articleTree = parsers_common.get_article_data(session, domain, articleDataDict["urls"][i], mainPage=False)

            # description
            curArtDesc = parsers_common.xpath_to_single(articleTree, '//div[@id="body1"]/div[@class="uudis_sisu"]', parent=True)
            articleDataDict["descriptions"].append(curArtDesc)

            # media
            curArtMedia = parsers_common.xpath_to_single(articleTree, '//div[@id="body1"]/div[@class="listeningItem"]/p/audio/source/@src')
            articleDataDict["images"].append(curArtMedia)

    # remove unwanted content
    k = 0
    while (k < len(articleDataDict["urls"])):
        rss_print.print_debug(__file__, "kontrollime kannet" + str(k + 1) + "/" + str(len(articleDataDict["urls"])) + ": " + articleDataDict["titles"][k], 3)
        if (articleDataDict["images"][k] == ""):
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
        else:
            k += 1

    return articleDataDict
