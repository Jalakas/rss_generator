#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod foorumi kõigi postituste nimekirja loomiseks
    """

    articleAuthors = parsers_common.xpath(pageTree, '//div/div[@class="inner"]/div[@class="postbody"]/p[@class="author"]/strong//text()')
    articleDescriptions = []
    articleImages = []
    articlePubDates = parsers_common.xpath(pageTree, '//div/div[@class="inner"]/div[@class="postbody"]/p/text()[2]')
    articleTitles = []
    articleUrls = parsers_common.xpath(pageTree, '//div/div[@class="inner"]/div[@class="postbody"]/p[@class="author"]/a/@href')

    articleDescriptionsParents = parsers_common.xpath(pageTree, '//div/div[@class="inner"]/div[@class="postbody"]/div[@class="content"]')  # as a parent

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # description
        curArtDescriptionsChilds = parsers_common.stringify_children(articleDescriptionsParents[i])
        curArtDescriptionsChilds = parsers_common.fixDrunkPost(curArtDescriptionsChilds)
        articleDescriptions.append(curArtDescriptionsChilds)

        # timeformat magic from "» 29 Dec 2017 13:46" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "» %d %m %Y %H:%M")
        articlePubDates[i] = curArtPubDate

        # title
        articleTitles.append("Arutelud" + " @" + domain)

        # url
        articleUrls[i] = articleUrls[i].split("&sid=")[0]

    # remove unwanted content
    j = 0
    while (j < min(len(articleUrls), maxArticleCount)):
        rss_print.print_debug(__file__, "kontrollime kannet: " + str(j + 1) + ", kokku: " + str(len(articleUrls)), 3)
        if (articleDescriptions[j].find("jumal ") >= 0 or articleDescriptions[j].find("Jumal ") >= 0):
            rss_print.print_debug(__file__, "eemaldame jumalat sisaldava kande: " + articleDescriptions[j], 0)

            articleDescriptions = parsers_common.del_if_set(articleDescriptions, j)
            articleImages = parsers_common.del_if_set(articleImages, j)
            articlePubDates = parsers_common.del_if_set(articlePubDates, j)
            articleTitles = parsers_common.del_if_set(articleTitles, j)
            articleUrls = parsers_common.del_if_set(articleUrls, j)
        else:
            j += 1

    return {"articleAuthors": articleAuthors,
            "articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
