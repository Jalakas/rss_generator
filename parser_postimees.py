#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/div/span[2]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/span/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/span/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # timeformat magic from "24.12.2017 17:51" to datetime()
        curArtPubDate = parsers_common.months_to_int(articleDataDict["pubDates"][i])
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%Y, %H:%M")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (getArticleBodies is True and i < maxArticleBodies):
            # load article into tree
            articleTree = parsers_common.get_article_data(domain, articleDataDict["urls"][i], False)

            # author
            curArtAuthor = parsers_common.xpath_to_single(articleTree, '//span[@class="article-authors__name"]/text()')
            articleDataDict["authors"].append(curArtAuthor)

            # description1 - enne pilti
            curArtDescChilds1 = ""
            if (curArtDescChilds1 == ""):
                curArtDescChilds1 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article"][1]/div[@class="flex"]//div[@class="article-body__item article-body__item--articleBullets"]', parent=True)
            if (curArtDescChilds1 == ""):
                curArtDescChilds1 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article-body article-body--left article-body--lead"]/div[@class="article-body__item article-body__item--articleBullets"]', parent=True)
            if (curArtDescChilds1 == ""):
                curArtDescChilds1 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article-body"]/div[@class="article-body__item article-body__item--articleBullets article-body--first-child"]', parent=True)

            # description2 - pildi ja kuulamise vahe
            curArtDescChilds2 = ""
            if (curArtDescChilds2 == ""):
                curArtDescChilds2 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"][1]', parent=True)
            if (curArtDescChilds2 == ""):
                curArtDescChilds2 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement"]', parent=True)
            if (curArtDescChilds2 == ""):
                curArtDescChilds2 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article-body"]/div[@class="article-body__item article-body__item--htmlElement"]', parent=True)
            if (curArtDescChilds2 == ""):
                curArtDescChilds2 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article"]//div[@class="article-body article-body--left"]', parent=True)
            if (curArtDescChilds2 == ""):
                curArtDescChilds2 = parsers_common.xpath_to_single(articleTree, '//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"]', parent=True)

            # description3 - pärast kuulamist
            curArtDescChilds3 = ""
            if (curArtDescChilds3 == ""):
                curArtDescChilds3 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article"][2]//div[@class="article-body article-body--left"]', parent=True)
            if (curArtDescChilds3 == ""):
                curArtDescChilds3 = parsers_common.xpath_to_single(articleTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement"][1]', parent=True)
            if (curArtDescChilds3 == ""):
                curArtDescChilds3 = parsers_common.xpath_to_single(articleTree, '//div[@class="article-body article-body--left article-body--lead"]', parent=True)

            # descriptions kontrollid
            if (articleDataDict["urls"][i].find("-kuulutused-") > 0):
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: kuulutused", 2)
            elif (articleDataDict["urls"][i].find("-karikatuur-") > 0):
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: karikatuur", 2)
            else:
                if (curArtDescChilds1 == ""):
                    rss_print.print_debug(__file__, "1. kirjeldusplokk on tühi. (Pildieelne kirjeldusplokk puudub?)", 2)
                else:
                    rss_print.print_debug(__file__, "curArtDescChilds1 = " + str(curArtDescChilds1), 3)
                if (curArtDescChilds2 == ""):
                    rss_print.print_debug(__file__, "2. kirjeldusplokk on tühi. (Pildi järel, enne kuulamist plokk puudub?)", 0)
                else:
                    rss_print.print_debug(__file__, "curArtDescChilds2 = " + str(curArtDescChilds2), 3)
                if (curArtDescChilds3 == ""):
                    rss_print.print_debug(__file__, "3. kirjeldusplokk on tühi. (Pärast kuulamist plokk puudub? - Ainult tellijale leht?)", 1)
                else:
                    rss_print.print_debug(__file__, "curArtDescChilds3 = " + str(curArtDescChilds3), 3)

            articleDataDict["descriptions"].append(curArtDescChilds1 + ' ' + curArtDescChilds2 + ' ' + curArtDescChilds3)

            # images
            curArtImg = ""
            if (curArtImg == ""):
                curArtImg = parsers_common.xpath_to_single(articleTree, '//figure/img[1]/@src')
            if (curArtImg == ""):
                rss_print.print_debug(__file__, "1. pilditüüpi ei leitud", 2)
                curArtImg = parsers_common.xpath_to_single(articleTree, '//div[@class="article-body__item article-body__item--image  "]//figure/img[1]/@src')
            if (curArtImg == ""):
                rss_print.print_debug(__file__, "2. pilditüüpi ei leitud", 2)
                curArtImg = parsers_common.xpath_to_single(articleTree, '/html/body/article/div[@class="article-superheader article-superheader--figure"]/div[@class="article-superheader__background"]/@style')
                curArtImg = curArtImg.split("url('")[-1].strip("');")
            if (curArtImg == ""):
                rss_print.print_debug(__file__, "3. pilditüüpi ei leitud", 2)
                curArtImg = parsers_common.xpath_to_single(articleTree, '//meta[@property="og:image"]/@content')
            # images kontroll
            if (articleDataDict["urls"][i].find("-kuulutused-") < 0):
                if (curArtImg == ""):
                    rss_print.print_debug(__file__, "ühtegi pilditüüpi ei leitud", 0)
                else:
                    rss_print.print_debug(__file__, "curArtImg = " + str(curArtImg), 3)
            articleDataDict["images"].append(curArtImg)

    return articleDataDict
