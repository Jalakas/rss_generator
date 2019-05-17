#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Avaliku teenistuse "Tartu" RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod saidi pakkumiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleTitles = parsers_common.xpath(pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[1]/text()')
    articleUrls = parsers_common.xpath(pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[5]/div[1]/a/@href')

    articleDescName = parsers_common.xpath(pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[2]/div[1]/text()')
    articleDescLoc = parsers_common.xpath(pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[4]/div[1]/text()')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # description
        try:
            articleDescriptions.append(parsers_common.toPlaintext(articleDescName[i]) + "<br>" + parsers_common.toPlaintext(articleDescLoc[i]))
        except Exception:
            rss_print.print_debug(__file__, "leht on tuksis, lisame tühja kirjelduse")
            articleDescriptions.append(" ")

        # title
        articleTitles[i] = parsers_common.toPlaintext(articleTitles[i]).capitalize()

    # remove non "Tartu" location lines
    retArticleDescriptions = []
    retArticleImages = []
    retArticlePubDates = []
    retArticleTitles = []
    retArticleUrls = []

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        if ('Tartu' in articleDescriptions[i]):
            retArticleDescriptions.append(articleDescriptions[i])
            # retArticleImages.append(articleImages[i])
            # retArticlePubDates.append(articlePubDates[i])
            retArticleTitles.append(articleTitles[i])
            retArticleUrls.append(articleUrls[i])

    return {"articleDescriptions": retArticleDescriptions,
            "articleImages": retArticleImages,
            "articlePubDates": retArticlePubDates,
            "articleTitles": retArticleTitles,
            "articleUrls": retArticleUrls,
           }
