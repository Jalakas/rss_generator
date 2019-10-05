#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//table[@class="views-table cols-5"]/tbody/tr', parent=True)
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[1]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[5]/div[1]/a/@href')

    # remove unwanted content
    dictWhitelist = ['Tartu', 'Türi']
    dictCond = "in"
    dictField = "descriptions"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictWhitelist=dictWhitelist)

    return articleDataDict
