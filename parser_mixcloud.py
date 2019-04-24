#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

# import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod kõigi objektide nimekirja loomiseks
    """

    articleDescriptions = pageTree.xpath('//main/div[1]/div/div/section[@class="card cf"]//h1/a/span/@title')
    articleIds = []
    articleImages = pageTree.xpath('//main/div[1]/div/div/section[@class="card cf"]//a/div/img/@scr')
    articlePubDates = []
    articleTitles = pageTree.xpath('//main/div[1]/div/div/section[@class="card cf"]//h1/a/span/@title')
    articleUrls = pageTree.xpath('//main/div[1]/div/div/section[@class="card cf"]//h1/a/@href')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # get unique id from articleUrl
        articleIds.append(articleUrls[i].rstrip("/"))

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
