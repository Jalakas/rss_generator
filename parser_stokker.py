#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product_camp_box w"]/a/div[@class="product_camp"]/div[@class="leftC"]/div/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product_camp_box w"]/a/div[@class="product_camp"]/div[@class="leftC"]/h3/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="product_camp_box w"]/a/@href')

    articlePrices = parsers_common.xpath_to_list(pageTree, '//div[@class="product_camp_box w"]/div[@class="priceCont"]', parent=True)
    articleDescriptions = parsers_common.xpath_to_list(pageTree, '//div[@class="product_camp_box w"]/a/div[@class="product_camp"]/div[@class="leftC"]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtPrice = articlePrices[i]
        curArtDesc = articleDescriptions[i]
        articleDataDict["descriptions"].append(curArtPrice + curArtDesc)

    return articleDataDict
