#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/figure/a/@data-original')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/div/div/p/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/div/div/p/a/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/div[@class="offers-thumb__article-helper "]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

    return articleDataDict
