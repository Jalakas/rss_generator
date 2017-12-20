#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Teabeleht RSS-voo sisendite parsimine
"""

from lxml import html
import parsers_common


def getArticleListsFromHtml(htmlPage, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """
    tree = html.fromstring(htmlPage)

    articleDescriptions = tree.xpath('//div[@class="nspArt nspCol1"]/div[@class="gkArtContentWrap"]/p[1]/text()')
    articleIds = []
    articleImages = tree.xpath('//div[@class="nspArt nspCol1"]/a/img/@src')
    articlePubDates = []
    articleTitles = tree.xpath('//div[@class="nspArt nspCol1"]/div[@class="gkArtContentWrap"]/h4/a/text()')
    articleUrls = tree.xpath('//div[@class="nspArt nspCol1"]/div[@class="gkArtContentWrap"]/h4/a/@href')
    articleUrls = [domain + elem for elem in articleUrls]

    # todo(reading times from articles is BROKEN and maybe useless too)
    get_article_bodies = False

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # generate unique id from articleUrl
        articleIds.append(parsers_common.urlToHash(articleUrl))

        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articleTree = parsers_common.getArticleData(articleUrl)

            # timeformat magic from "Avaldatud: Neljapäev, 14 Detsember 2017 12:46" to datetime()
            # curArtPubDate = parsers_common.treeExtract(articleTree, '//div[@class="kakk-postheadericons kakk-metadata-icons"]/span/::before/text()')  # katki
            curArtPubDate = parsers_common.treeExtract(articleTree, '//span[@class="kakk-postdateicon"]//text()')
            curArtPubDate = parsers_common.longMonthsToNumber(curArtPubDate.split(',')[1])
            curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d %m %Y %H:%M")
            articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
