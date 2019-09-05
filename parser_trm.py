#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="image-cell"]/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="description-cell"]/h2/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="description-cell"]/a/@href')

    articlePriceParents = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="price-cell"]', parent=True)
    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="description-cell"]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtPriceChilds = parsers_common.stringify_index_children(articlePriceParents, i)
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtPriceChilds + curArtDescChilds)

    return articleDataDict
