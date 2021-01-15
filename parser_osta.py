#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//article/ul/li/figure/div[@class="offers-thumb__article-helper "]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//article/ul/li/figure/figure/a[@class="lazy"]/@data-original')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//article/ul/li/figure/div/div/p/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//article/ul/li/figure/div/div/p/a/@href')

    return articleDataDict
