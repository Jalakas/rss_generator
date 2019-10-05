#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/div/p/text()')
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/p/img/@src')
    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/@title')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/div/h3/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # timeformat magic from "03.01.2018 11:09.08 [Tanel]" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = curArtPubDate.split('[')[-2].strip()
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M.%S")
        articleDataDict["pubDates"][i] = curArtPubDate

    return articleDataDict
