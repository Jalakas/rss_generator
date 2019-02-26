#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    JT RSS-voo sisendite parsimine
"""

import makereq
import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = pageTree.xpath('//ul[@class="search-results"]/li/div/div/span[2]/text()')
    articleTitles = pageTree.xpath('//ul[@class="search-results"]/li/div/span/a/text()')
    articleUrls = pageTree.xpath('//ul[@class="search-results"]/li/div/span/a/@href')

    get_article_bodies = True

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from ArticleUrl
        articleIds.append(articleUrl.split('/')[-2])

        # timeformat magic from "24.12.2017 17:51" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.longMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y, %H:%M")
        articlePubDates[i] = curArtPubDate

        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articleTree = makereq.getArticleData(articleUrl)
            articleTreeBuf = makereq.getArticleData(articleUrl)

            # description1 - enne pilti kokkuvõte
            curArtDescParent1 = parsers_common.treeExtract(articleTree,
            '//article/div[@class="article"][1]/div[@class="flex"]//div[@class="article-body__item article-body__item--articleBullets"]')  # as a parent
            curArtDescChilds1 = parsers_common.stringify_children(curArtDescParent1)
            if (curArtDescChilds1 == ""):
                curArtDescParent1 = parsers_common.treeExtract(articleTree,
                '//div/div[@itemprop="description"]/p')  # as a parent
                #'//article/div[@class="flex"][1]//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"]/p')  # as a parent
                curArtDescChilds1 = parsers_common.stringify_children(curArtDescParent1)
                if (curArtDescChilds1 == ""):
                    print("parser_jt: 1. kirjeldusplokk on tühi, alternatiiv ka tühi!")

            # description2 - sissejuhatus pärast pilti
            articleTree = articleTreeBuf
            curArtDescParent2 = parsers_common.treeExtract(articleTree,
            '//article/div[@class="article"]//div[@class="article-body__item article-body__item--htmlElement"]')  # as a parent
            curArtDescChilds2 = parsers_common.stringify_children(curArtDescParent2)
            if (curArtDescChilds2 == ""):
                curArtDescParent2 = parsers_common.treeExtract(articleTree,
                '//div[@class="article"]/div[@class="flex--equal-width"]/div[@class="article-body"]')  # as a parent
                #'//article/div[@class="article"]//div[@class="flex--equal-width"]')  # as a parent
                curArtDescChilds2 = parsers_common.stringify_children(curArtDescParent2)
                if (curArtDescChilds2 == ""):
                    print("parser_jt: 2. kirjeldusplokk on tühi, alternatiiv ka tühi! (Ainult tellijale leht?)")

            # description3 - tasuta artikli sisu
            articleTree = articleTreeBuf
            curArtDescParent3 = parsers_common.treeExtract(articleTree, '//article/div[@class="article"][2]//div[@class="article-body"]')  # as a parent
            curArtDescChilds3 = parsers_common.stringify_children(curArtDescParent2)
            if (curArtDescChilds3 == ""):
                curArtDescParent3 = parsers_common.treeExtract(articleTree, '//div[@class="article"][2]//div[@class="flex--equal-width"]/div[@class="article-body"]')  # as a parent
                curArtDescChilds3 = parsers_common.stringify_children(curArtDescParent2)
                if (curArtDescChilds3 == ""):
                    print("parser_jt: 3. kirjeldusplokk on tühi, alternatiiv ka tühi! (Ainult tellijale leht?)")

            articleDescriptions.append(curArtDescChilds1 + ' ' + curArtDescChilds2 + ' ' + curArtDescChilds3)

            # image
            curArtImg = parsers_common.treeExtract(articleTree, '//div[@class="article-body__item article-body__item--image  "]//figure/img[1]/@src') or "//"
            if (curArtImg == "//"):
                curArtImg = parsers_common.treeExtract(articleTree, '//figure/img[1]/@src') or "//"
                if (curArtImg == "//"):
                    print("parser_jt: esimest pilditüüpi ning teist pilditüüpi ei leitud!")
            curArtImg = "http:" + curArtImg
            articleImages.append(curArtImg)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
