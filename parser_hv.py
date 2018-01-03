#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HV RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod HV uudiste nimekirja loomiseks
    """

    articleDescriptions = pageTree.xpath('//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/div/p/text()')
    articleIds = []
    articleImages = pageTree.xpath('//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/p/img/@src')
    articlePubDates = []
    articleTitles = pageTree.xpath('//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/div/h3/text()')
    articleUrls = pageTree.xpath('//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/@href')

    articlePubDatesRaw = pageTree.xpath('//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/@title')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl.split('?t=')[-1])

        # description
        articleDescriptions[i] = parsers_common.toPlaintext(articleDescriptions[i])

        # timeformat magic from "03.01.2018 11:09.08 [Tanel]" to datetime()
        curArtPubDate = articlePubDatesRaw[i].split('[')[-2].strip()
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y %H:%M.%S")
        articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
