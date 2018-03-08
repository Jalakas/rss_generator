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
    articleImages = pageTree.xpath('//div[@class="image_container"]/a/img/@img')
    articlePubDates = []
    articleTitles = pageTree.xpath('//div[@class="article_content"]/div[@class="article_title_wrapper"]/a[1]/text()')
    articleUrls = pageTree.xpath('//div[@class="article_content"]/div[@class="article_title_wrapper"]/a[1]/@href')

    get_article_bodies = True

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # generate unique id from ArticleUrl
        articleIds.append(parsers_common.urlToHash(articleUrl))

        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articleTree = makereq.getArticleData(articleUrl)

            # description
            curArtDescParent = parsers_common.treeExtract(articleTree, '//div[@class="article full_article column"]/div[@class="article_content"]')  # as a parent
            curArtDescChilds = parsers_common.stringify_children(curArtDescParent)
            articleDescriptions.append(curArtDescChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
