#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/div[@class="offers-thumb__article-helper "]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/figure/a/@data-original')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/div/div/p/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//main/div/ul/li/figure/div/div/p/a/@href')

    return articleDataDict
