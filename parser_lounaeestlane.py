#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Lõunaeestlane RSS-voo sisendite parsimine
"""

import makereq
import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = pageTree.xpath('//div[@class="col-sm-6"]/div[@class="post-item"]/a/div/img/@src')
    articlePubDates = []
    articleTitles = pageTree.xpath('//div[@class="col-sm-6"]/div[@class="post-item"]/a/h3/text()')
    articleUrls = pageTree.xpath('//div[@class="col-sm-6"]/div[@class="post-item"]/a/@href')

    get_article_bodies = False

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # generate unique id from ArticleUrl
        articleIds.append(parsers_common.urlToHash(articleUrl))

        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articleTree = makereq.getArticleData(articleUrl)

            # get first paragraph as header
            curArtDesc = parsers_common.treeExtract(articleTree, '//div[@class="col-sm-9"]/p[1]/strong/text()')
            articleDescriptions.append(curArtDesc)

            # timeformat magic from "Avaldatud: 14 detsember, 2017" to datetime()
            curArtPubDate = parsers_common.treeExtract(articleTree, '//div[@class="col-sm-9"]/div[@class="page-header"]/em/text()')
            curArtPubDate = parsers_common.longMonthsToNumber(curArtPubDate.split(':')[1])
            curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d %m, %Y")
            articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
