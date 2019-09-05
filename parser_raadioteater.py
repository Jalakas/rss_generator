#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@id="body1"]/h1/a/@href')

    articleUrlParents = parsers_common.xpath_to_list(pageTree, '//div[@id="body1"]/h1/a', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # titles
        curArtTitlesChilds = parsers_common.stringify_index_children(articleUrlParents, i)
        articleDataDict["titles"].append(curArtTitlesChilds)

        if (getArticleBodies is True and i < maxArticleBodies):
            # load article into tree
            articleTree = parsers_common.get_article_data(domain, articleDataDict["urls"][i], False)

            # description
            curArtDescChilds = parsers_common.xpath_to_single(articleTree, '//div[@id="body1"]/div[@class="uudis_sisu"]', parent=True)
            articleDataDict["descriptions"].append(curArtDescChilds)

            # media
            curArtPubImage = parsers_common.xpath_to_single(articleTree, '//div[@id="body1"]/div[@class="listeningItem"]/p/audio/source/@src')
            articleDataDict["images"].append(curArtPubImage)

    # remove unwanted content
    k = 0
    while (k < len(articleDataDict["urls"])):
        rss_print.print_debug(__file__, "kontrollime kannet" + str(k + 1) + "/" + str(len(articleDataDict["urls"])) + ": " + articleDataDict["titles"][k], 3)
        if (articleDataDict["images"][k] == ""):
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
        else:
            k += 1

    return articleDataDict
