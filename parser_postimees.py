#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    articleDataDict["authors"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="search-result__authors"]/text()')
    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/div/span[2]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/span/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/span/a/@href')

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        # timeformat magic from "24.12.2017 17:51" to datetime()
        curArtPubDate = parsers_common.monthsToNumber(articleDataDict["pubDates"][i])
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y, %H:%M")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (getArticleBodies is True) and (i < maxArticleCount):
            # load article into tree
            articleTree = parsers_common.getArticleData(domain, articleDataDict["urls"][i], False)

            # description1 - enne pilti kokkuvõte
            if (True):
                curArtDescChilds1 = parsers_common.xpath_parent_to_single(articleTree, '//article/div[@class="article"][1]/div[@class="flex"]//div[@class="article-body__item article-body__item--articleBullets"]')

            # description2 - sissejuhatus pärast pilti
            if (True):
                curArtDescChilds2 = parsers_common.xpath_parent_to_single(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"][1]')
            if (curArtDescChilds2 == ""):
                curArtDescChilds2 = parsers_common.xpath_parent_to_single(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement"]')
            if (curArtDescChilds2 == ""):
                curArtDescChilds2 = parsers_common.xpath_parent_to_single(articleTree, '//article/div[@class="article"]//div[@class="article-body article-body--left"]')
            curArtDescChilds2 = parsers_common.rstrip_string(curArtDescChilds2, "<")

            # description3 - tasuta artikli sisu
            if (True):
                curArtDescChilds3 = parsers_common.xpath_parent_to_single(articleTree, '//div[@class="article"][2]//div[@class="article-body article-body--left"]')
            if (curArtDescChilds3 == ""):
                curArtDescChilds3 = parsers_common.xpath_parent_to_single(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement"][1]')

            # description
            articleDataDict["descriptions"].append(curArtDescChilds1 + ' ' + curArtDescChilds2 + ' ' + curArtDescChilds3)

            # image
            if (True):
                curArtImg = parsers_common.xpath_to_single(articleTree, '//figure/img[1]/@src')
            if (curArtImg == ""):
                rss_print.print_debug(__file__, "1. pilditüüpi ei leitud", 1)
                curArtImg = parsers_common.xpath_to_single(articleTree, '//div[@class="article-body__item article-body__item--image  "]//figure/img[1]/@src')
            if (curArtImg == ""):
                rss_print.print_debug(__file__, "2. pilditüüpi ei leitud", 1)
                curArtImg = parsers_common.xpath_to_single(articleTree, '//meta[@property="og:image"]/@content')
            articleDataDict["images"].append(curArtImg)

            #  kontrollid
            if (curArtDescChilds1 == ""):
                rss_print.print_debug(__file__, "1. kirjeldusplokk on tühi. (Pildieelne kirjeldusplokk puudub?)", 2)
            else:
                rss_print.print_debug(__file__, "curArtDescChilds1 = " + str(curArtDescChilds1), 3)
            if (curArtDescChilds2 == ""):
                if (articleDataDict["urls"][i].find("-kuulutused-") < 0):
                    rss_print.print_debug(__file__, "2. kirjeldusplokk on tühi. (Pildi järel puudub sissejuhatus?)", 1)
            else:
                rss_print.print_debug(__file__, "curArtDescChilds2 = " + str(curArtDescChilds2), 3)
            if (curArtDescChilds3 == ""):
                if (articleDataDict["urls"][i].find("-kuulutused-") < 0):
                    rss_print.print_debug(__file__, "3. kirjeldusplokk on tühi. (Ainult tellijale leht?)", 1)
            else:
                rss_print.print_debug(__file__, "curArtDescChilds3 = " + str(curArtDescChilds3), 3)
            if (curArtImg == ""):
                rss_print.print_debug(__file__, "ühtegi pilditüüpi ei leitud", 0)
            else:
                rss_print.print_debug(__file__, "curArtImg = " + str(curArtImg), 3)

    return articleDataDict
