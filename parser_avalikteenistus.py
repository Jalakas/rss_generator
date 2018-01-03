#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Avaliku teenistuse "Tartu" RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod saidi pakkumiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    # articleImages = []
    # articlePubDates = []
    articleTitles = pageTree.xpath('//table[@class="views-table cols-5"]/tbody/tr/td[1]/text()')
    articleUrls = pageTree.xpath('//table[@class="views-table cols-5"]/tbody/tr/td[5]/div[1]/a/@href')

    articleDescName = pageTree.xpath('//table[@class="views-table cols-5"]/tbody/tr/td[2]/div[1]/text()')
    articleDescLoc = pageTree.xpath('//table[@class="views-table cols-5"]/tbody/tr/td[4]/div[1]/text()')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl.split('/')[-1])

        # description
        articleDescriptions.append(parsers_common.toPlaintext(articleDescName[i]) + "<br>" + parsers_common.toPlaintext(articleDescLoc[i]))

        # title
        articleTitles[i] = parsers_common.toPlaintext(articleTitles[i]).capitalize()

    # remove non "Tartu" location lines
    retArticleDescriptions = []
    retArticleIds = []
    retArticleImages = []
    retArticlePubDates = []
    retArticleTitles = []
    retArticleUrls = []
    for i in range(0, len(articleUrls)):
        if ('Tartu' in articleDescriptions[i]):
            retArticleDescriptions.append(articleDescriptions[i])
            retArticleIds.append(articleIds[i])
            # retArticleImages.append(articleImages[i])
            # retArticlePubDates.append(articlePubDates[i])
            retArticleTitles.append(articleTitles[i])
            retArticleUrls.append(articleUrls[i])

    return {"articleDescriptions": retArticleDescriptions,
            "articleIds": retArticleIds,
            "articleImages": retArticleImages,
            "articlePubDates": retArticlePubDates,
            "articleTitles": retArticleTitles,
            "articleUrls": retArticleUrls,
           }
