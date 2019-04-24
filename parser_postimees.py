#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod saidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = pageTree.xpath('//ul[@class="search-results"]/li/div/div/span[2]/text()')
    articleTitles = pageTree.xpath('//ul[@class="search-results"]/li/div/span/a/text()')
    articleUrls = pageTree.xpath('//ul[@class="search-results"]/li/div/span/a/@href')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # get unique id from ArticleUrl
        articleIds.append(articleUrls[i].split('/')[-2])

        # timeformat magic from "24.12.2017 17:51" to datetime()
        curArtPubDate = articlePubDates[i]
        curArtPubDate = parsers_common.longMonthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y, %H:%M")
        articlePubDates[i] = curArtPubDate

        if (getArticleBodies is True):
            # load article into tree
            articleTree = parsers_common.getArticleData(articleUrls[i])
            articleTreeBuf = articleTree

            # laeme topelt, kuna parser ei suutnud muidu samast dokumendist asju leida
            # articleTreeBuf = parsers_common.getArticleData(articleUrls[i]

            # description1 - enne pilti kokkuvõte
            curArtDescParent1 = parsers_common.treeExtract(articleTree, '//article/div[@class="article"][1]/div[@class="flex"]//div[@class="article-body__item article-body__item--articleBullets"]')  # as a parent
            curArtDescriptionsChilds1 = parsers_common.stringify_children(curArtDescParent1)
            rss_print.print_debug(__file__, "1. kirjeldusplokk on tühi (Pildieelne kirjeldusplokk puudub?)", 2)

            # description2 - sissejuhatus pärast pilti
            articleTree = articleTreeBuf
            curArtDescParent2 = parsers_common.treeExtract(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"][1]')  # as a parent
            curArtDescriptionsChilds2 = parsers_common.stringify_children(curArtDescParent2)
            if (curArtDescriptionsChilds2 == ""):
                curArtDescParent2 = parsers_common.treeExtract(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement"]')  # as a parent
                # '//article/div[@class="article"]//div[@class="flex--equal-width"]')  # as a parent
                curArtDescriptionsChilds2 = parsers_common.stringify_children(curArtDescParent2)
                if (curArtDescriptionsChilds2 == ""):
                    rss_print.print_debug(__file__, "2. kirjeldusplokk on tühi, alternatiiv ka tühi (Pildi järel puudub sissejuhatus?)")

            # description3 - tasuta artikli sisu
            articleTree = articleTreeBuf
            curArtDescParent3 = parsers_common.treeExtract(articleTree, '//div[@class="article"][2]//div[@class="article-body article-body--left"]')  # as a parent
            curArtDescriptionsChilds3 = parsers_common.stringify_children(curArtDescParent3)
            if (curArtDescriptionsChilds3 == ""):
                rss_print.print_debug(__file__, "3. kirjeldusploki esimest varianti ei leitud, proovime teist", 2)
                curArtDescParent3 = parsers_common.treeExtract(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement"][1]')  # as a parent
                curArtDescriptionsChilds3 = parsers_common.stringify_children(curArtDescParent3)
                if (curArtDescriptionsChilds3 == ""):
                    rss_print.print_debug(__file__, "3. kirjeldusplokk on tühi, alternatiiv ka tühi (Ainult tellijale leht?)")

            articleDescriptions.append(
                curArtDescriptionsChilds1 + ' <br/> ' + curArtDescriptionsChilds2 + ' <br/> ' + curArtDescriptionsChilds3)

            # image
            curArtImg = parsers_common.treeExtract(articleTree, '//figure/img[1]/@src') or "//"
            if (curArtImg == "//"):
                rss_print.print_debug(__file__, "1. pilditüüpi ei leitud", 1)
                curArtImg = parsers_common.treeExtract(articleTree, '//div[@class="article-body__item article-body__item--image  "]//figure/img[1]/@src') or "//"
                if (curArtImg == "//"):
                    rss_print.print_debug(__file__, "2. pilditüüpi ei leitud", 1)
                    # mitme pildi galerii avapilt
                    curArtImg = parsers_common.treeExtract(articleTree, '//div[@class="VueCarousel-slide gallery-image"]/@style') or "//"
                    if (curArtImg == "//"):
                        rss_print.print_debug(__file__, "ühtegi pilditüüpi ei leitud", 0)
            curArtImg = "http:" + curArtImg
            articleImages.append(curArtImg)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
