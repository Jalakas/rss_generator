#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HV RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod HV uudiste nimekirja loomiseks
    """

    articleDescriptions = parsers_common.xpath(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/div/p/text()')
    articleImages = parsers_common.xpath(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/p/img/@src')
    articlePubDates = parsers_common.xpath(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/@title')
    articleTitles = parsers_common.xpath(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/div/h3/text()')
    articleUrls = parsers_common.xpath(pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/@href')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # description
        articleDescriptions[i] = parsers_common.toPlaintext(articleDescriptions[i])

        # timeformat magic from "03.01.2018 11:09.08 [Tanel]" to datetime()
        curArtPubDate = articlePubDates[i].split('[')[-2].strip()
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y %H:%M.%S")
        articlePubDates[i] = curArtPubDate

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
