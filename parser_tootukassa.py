#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Töötukassa RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod saidi pakkumiste nimekirja loomiseks
    """

    articleDescriptions = pageTree.xpath('//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/p/text()')
    articleIds = []
    articleImages = []
    articlePubDates = pageTree.xpath('//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="right-content"]/div[@class="application-date"][1]/text()')
    articleTitles = pageTree.xpath('//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/text()')
    articleUrls = pageTree.xpath('//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/@href')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        articleUrls[i] = articleUrls[i].split('?ref=')[0]

        # get unique id from articleUrl
        articleIds.append(articleUrls[i].split('-')[-1])

        # timeformat magic from "Avaldatud: 12.12.2017" to datetime()
        curArtPubDate = articlePubDates[i].split(': ')[1]
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
        articlePubDates[i] = curArtPubDate

        # title
        articleDescriptions[i] = parsers_common.toPlaintext(articleDescriptions[i]).capitalize()

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
