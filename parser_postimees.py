#!/usr/bin/env python3

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/div/span[2]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/span/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//ul[@class="search-results"]/li[@class="search-results__item"]/div[@class="flex"]/span/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # timeformat magic from "24.12.2017 17:51" to datetime()
        curArtPubDate = parsers_common.months_to_int(articleDataDict["pubDates"][i])
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%Y, %H:%M")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            pageTree = parsers_common.get_article_tree(session, domain, articleDataDict["urls"][i], noCache=False)

            # author
            curArtAuthor = parsers_common.xpath_to_single(pageTree, '//span[@class="article-authors__name"]/text()')
            articleDataDict["authors"].append(curArtAuthor)

            # description1 - enne pilti
            curArtDesc1 = ""
            if curArtDesc1 == "":
                curArtDesc1 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article"][1]/div[@class="flex"]//div[@class="article-body__item article-body__item--articleBullets"]', parent=True)
            if curArtDesc1 == "":
                curArtDesc1 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article-body article-body--left article-body--lead"]/div[@class="article-body__item article-body__item--articleBullets"]', parent=True)
            if curArtDesc1 == "":
                curArtDesc1 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article-body"]/div[@class="article-body__item article-body__item--articleBullets article-body--first-child"]', parent=True)

            # description2 - pildi ja kuulamise vahel
            curArtDesc2 = ""
            if curArtDesc2 == "":
                curArtDesc2 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"][1]', parent=True)
            if curArtDesc2 == "":
                curArtDesc2 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement"]', parent=True)
            if curArtDesc2 == "":
                curArtDesc2 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article-body"]/div[@class="article-body__item article-body__item--htmlElement"]', parent=True)
            if curArtDesc2 == "":
                curArtDesc2 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article"]//div[@class="article-body article-body--left"]', parent=True)
            if curArtDesc2 == "":
                curArtDesc2 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"]', parent=True)
            if curArtDesc2 == "":
                curArtDesc2 = parsers_common.xpath_to_single(pageTree, '//div[@itemprop="articleBody"]/div[@itemprop="description"]', parent=True)

            # description3 - pärast kuulamist
            curArtDesc3 = ""
            if curArtDesc3 == "":
                curArtDesc3 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article"][2]//div[@class="article-body article-body--left"]', parent=True)
            if curArtDesc3 == "":
                curArtDesc3 = parsers_common.xpath_to_single(pageTree, '//article/div[@class="article"][1]//div[@class="article-body__item article-body__item--htmlElement"][1]', parent=True)
            if curArtDesc3 == "":
                curArtDesc3 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body article-body--left article-body--lead"]', parent=True)

            # image
            curArtImg = ""
            if curArtImg == "":
                curArtImg = parsers_common.xpath_to_single(pageTree, '//figure/img[1]/@src')
            if curArtImg == "":
                curArtImg = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--image "]//figure/img[1]/@src')
            if curArtImg == "":
                curArtImg = parsers_common.xpath_to_single(pageTree, '/html/body/article/div[@class="article-superheader article-superheader--figure"]/div[@class="article-superheader__background"]/@style')
                curArtImg = curArtImg.split("url('")[-1].strip("');")
            if curArtImg == "":
                curArtImg = parsers_common.xpath_to_single(pageTree, '//meta[@property="og:image"]/@content')

            # kontrollid
            if articleDataDict["urls"][i].find("-kuulutused-") > 0:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: kuulutused", 2)
            elif articleDataDict["urls"][i].find("-karikatuur-") > 0:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: karikatuur", 2)
            else:
                if curArtDesc1 == "":
                    rss_print.print_debug(__file__, "1. kirjeldusplokk on tühi. (Pildieelne kirjeldusplokk puudub?)", 2)
                else:
                    rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc1, 3)
                if curArtDesc2 == "":
                    rss_print.print_debug(__file__, "2. kirjeldusplokk on tühi. (Pildi järel, enne kuulamist plokk puudub?)", 0)
                else:
                    rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 3)
                if curArtDesc3 == "":
                    rss_print.print_debug(__file__, "3. kirjeldusplokk on tühi. (Pärast kuulamist plokk puudub? - Ainult tellijale leht?)", 1)
                else:
                    rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 3)
                if curArtImg == "":
                    rss_print.print_debug(__file__, "pilti ei leitud.", 0)
                else:
                    rss_print.print_debug(__file__, "curArtImg = " + curArtImg, 3)

            curArtDesc = curArtDesc1 + ' ' + curArtDesc2 + ' ' + curArtDesc3
            curArtDesc = curArtDesc.replace('<span class="button--for-subscription"><span>Tellijale</span></span>', "")

            articleDataDict["descriptions"].append(curArtDesc)
            articleDataDict["images"].append(curArtImg)

    return articleDataDict
