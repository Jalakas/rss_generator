#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Töötukassa RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod saidi pakkumiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = pageTree.xpath('//table[@class="footable"]/tbody/tr/td[2]/text()')
    articleTitles = pageTree.xpath('//table[@class="footable"]/tbody/tr/td[1]/a/strong/text()')
    articleUrls = pageTree.xpath('//table[@class="footable"]/tbody/tr/td[1]/a/@href')

    articleDescName = pageTree.xpath('//table[@class="footable"]/tbody/tr/td[1]/text()[2]')
    articleDescLoc = pageTree.xpath('//table[@class="footable"]/tbody/tr/td[4]/text()')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl.split('-')[-1])

        # description
        articleDescriptions.append(parsers_common.toPlaintext(articleDescName[i]) + "<br>" + parsers_common.toPlaintext(articleDescLoc[i]))

        # timeformat magic from "12.12.2017" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y")
        articlePubDates[i] = curArtPubDate

        # title
        articleTitles[i] = parsers_common.toPlaintext(articleTitles[i]).capitalize()

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
