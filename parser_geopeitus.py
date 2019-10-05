#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr', parent=True)
    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # timeformat magic from "29.08.19" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%y")
        articleDataDict["pubDates"][i] = curArtPubDate

    # remove unwanted content
    dictWhitelist = ["Tartu"]
    dictCond = "in"
    dictField = "descriptions"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictWhitelist=dictWhitelist)

    return articleDataDict
