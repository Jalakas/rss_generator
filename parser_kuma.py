#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Kuma RSS-voo sisendite parsimine
"""

import makereq
import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = pageTree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-excerpt"]/p/text()')
    articleIds = []
    articleImages = pageTree.xpath('//div[@class="news-list-media"]/img/@src')
    articleImages = parsers_common.domainUrls(domain, articleImages)
    articlePubDates = []
    articleTitles = pageTree.xpath('//div[@class="news-list-item-wrapper"]/h3/a/text()')
    articleUrls = pageTree.xpath('//div[@class="news-list-item-wrapper"]/h3/a/@href')
    articleUrls = parsers_common.domainUrls(domain, articleUrls)

    articlePubDay = pageTree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/text()[1]')
    articlePubMonth = pageTree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/span[@class="month"]/text()')
    articlePubYear = pageTree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/text()[2]')

    get_article_bodies = True

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # generate unical id from ArticleUrl
        articleIds.append(parsers_common.urlToHash(articleUrl))

        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articleTree = makereq.getArticleData(articleUrl)

            # descriptions
            curArtDescParent = parsers_common.treeExtract(articleTree, '//div[@class="news-single-item"]/div[@class="news-single-content"]')  # as a parent
            curArtDescChilds = parsers_common.stringify_children(curArtDescParent)
            articleDescriptions[i] = curArtDescChilds

            # timeformat magic from "13 dets  17" to datetime()
            curArtPubDate = parsers_common.treeExtract(articleTree, '//div[@class="news-single-timedata"]/text()')
            curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
            curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d %m %y")
            articlePubDates.append(curArtPubDate)
        else:
            if i < len(articlePubYear) and (int(articlePubYear[i].strip()) > 2016):
                curYear = articlePubYear[i].strip()
            curArtPubDate = articlePubDay[i].strip() + " " + articlePubMonth[i].strip() + " " + curYear
            curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d %m %Y")
            articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articleIds": articleIds,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
