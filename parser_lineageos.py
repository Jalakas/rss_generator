#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//li[@class="collection-item flex-dynamic"]/a/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//li[@class="collection-item flex-dynamic"]/span/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//li[@class="collection-item flex-dynamic"]/a/@href')

    return articleDataDict
