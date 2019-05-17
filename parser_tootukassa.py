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

    articleDescriptions = []
    articleImages = []
    articlePubDates = parsers_common.xpath(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="right-content"]/div[@class="application-date"][1]/text()')
    articleTitles = parsers_common.xpath(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/text()')
    articleUrls = parsers_common.xpath(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/@href')

    articleDescriptionsParents = parsers_common.xpath(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/p')  # as a parent

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # clean up url
        articleUrls[i] = articleUrls[i].split('?ref=')[0]

        # timeformat magic from "Avaldatud: 12.12.2017" to datetime()
        curArtPubDate = articlePubDates[i].split(': ')[1]
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
        articlePubDates[i] = curArtPubDate

        # description
        curArtDescriptionsChilds = parsers_common.stringify_children(articleDescriptionsParents[i])
        articleDescriptions.append(curArtDescriptionsChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
