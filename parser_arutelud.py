#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Arutelud RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod foorumi kõigi postituste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = pageTree.xpath('//div/div[@class="inner"]/div[@class="postbody"]/p/text()[2]')
    articleTitles = pageTree.xpath('//div/div[@class="inner"]/div[@class="postbody"]/p[@class="author"]/strong//text()')
    articleUrls = pageTree.xpath('//div/div[@class="inner"]/div[@class="postbody"]/p[@class="author"]/a/@href')

    articleDescriptionsParents = pageTree.xpath('//div/div[@class="inner"]/div[@class="postbody"]/div[@class="content"]')  # as a parent

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # get unique id from articleUrl
        articleIds.append(articleUrls[i].split('#p')[-1])

        # description
        curArtDescriptionsChilds = parsers_common.stringify_children(articleDescriptionsParents[i])
        articleDescriptions.append(curArtDescriptionsChilds)

        # title
        articleTitles[i] = articleTitles[i] + " @" + domain

        # timeformat magic from "» 29 Dec 2017 13:46" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "» %d %m %Y %H:%M")
        articlePubDates[i] = curArtPubDate

        if (articleDescriptions[i].find("jumal") > 0 or articleDescriptions[i].find("Jumal") > 0):
            rss_print.print_debug(__file__, "Eemaldame jumalat sisaldava kande")
            i = i - 1

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
