#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, session):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="image-cell"]/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="description-cell"]/h2/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="description-cell"]/a/@href')

    articlePrices = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="price-cell"]', parent=True)
    articleDescriptions = parsers_common.xpath_to_list(pageTree, '//div[@class="product"]/div[@class="description-cell"]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtPrice = articlePrices[i]
        curArtDesc = articleDescriptions[i]
        articleDataDict["descriptions"].append(curArtPrice + curArtDesc)

    return articleDataDict
