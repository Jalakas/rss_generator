#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Arutelud RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod foorumi kõigi postituste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = pageTree.xpath('//div/div[@class="inner"]/div[@class="postbody"]/p/text()[2]')
    articleTitles = pageTree.xpath('//div/div[@class="inner"]/div[@class="postbody"]/p[@class="author"]/strong//text()')
    articleUrls = pageTree.xpath('//div/div[@class="inner"]/div[@class="postbody"]/p[@class="author"]/a/@href')
    articleUrls = parsers_common.domainUrls(domain, articleUrls)

    articleDescriptionsParents = pageTree.xpath('//div/div[@class="inner"]/div[@class="postbody"]/div[@class="content"]')  # as a parent

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl.split('#p')[-1])

        # description
        curArtDescChilds = parsers_common.stringify_children(articleDescriptionsParents[i])
        articleDescriptions.append(curArtDescChilds)

        # title
        articleTitles[i] = articleTitles[i] + " @" + domain

        # timeformat magic from "» 29 Dec 2017 13:46" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "» %d %m %Y %H:%M")
        articlePubDates[i] = curArtPubDate

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
