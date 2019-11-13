#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//div[@class="c950ig-2 dPzYkG"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//img[@class=" sc-1kym84g-1 IncJl lazyloading"]/@src')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//h2[@class="c950ig-3 ktOarF"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//a[@class="sc-1kym84g-0 dxESGf c950ig-0 eUNpOJ"]/@href')

    return articleDataDict
