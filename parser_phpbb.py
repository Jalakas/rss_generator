#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    maxArticleCount = min(maxArticleCount, 15)
    maxArticlePostsCount = round(150 / maxArticleCount)  # set 0 for all posts

    articlePreLoopTitles = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[1]/text()')
    articlePreLoopUrls = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[1]/@href')

    if (len(articlePreLoopUrls) < 1):
        rss_print.print_debug(__file__, "ei leidnud nimekirjast ühtegi aktiivset teemat", 0)
        if (domain == "http://arutelud.com"):
            articlePreLoopTitles.append("Arutelud")
            articlePreLoopUrls.append("http://arutelud.com/viewtopic.php?f=3&t=4&sd=d&sk=t&st=7")

    # teemade läbivaatamine
    for i in parsers_common.articleUrlsRange(articlePreLoopUrls):
        # teemalehe sisu hankimine
        if (getArticleBodies is True) and (i < maxArticleCount):
            articlePreLoopUrls[i] = articlePreLoopUrls[i].split("&sid=")[0]
            articlePostsTree = parsers_common.getArticleData(domain, articlePreLoopUrls[i] + "&start=100000", True)  # True teeb alati päringu

            articleLoopAuthors = parsers_common.xpath_to_list(articlePostsTree, '//div/div[@class="inner"]/div[@class="postbody"]/div/p[@class="author"]/span/strong/a/text()')
            articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//div/div[@class="inner"]/div[@class="postbody"]/div/p[@class="author"]/text()[1]')
            if len(articleLoopPubDates) == 0:
                rss_print.print_debug(__file__, "ei suutnud hankida ühtegi aega", 0)
            else:
                if (len(str(articleLoopPubDates[0]).strip()) < 5):
                    rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articleLoopPubDates[0] + "', proovime alternatiivi...", 1)
                    articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//div/div[@class="inner"]/div[@class="postbody"]/div/p[@class="author"]/text()[2]')
                if (len(str(articleLoopPubDates[0]).strip()) < 5):
                    rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articleLoopPubDates[0] + "'", 0)
                else:
                    rss_print.print_debug(__file__, "hangitud aeg[0]: '" + articleLoopPubDates[0] + "'", 4)
            articleLoopUrls = parsers_common.xpath_to_list(articlePostsTree, '//div/div[@class="inner"]/div[@class="postbody"]/div/p[@class="author"]/a/@href')
            articleLoopDescriptionsParents = parsers_common.xpath_to_list(articlePostsTree, '//div/div[@class="inner"]/div[@class="postbody"]/div/div[@class="content"]')  # as a parent

            # postituste läbivaatamine
            for j in parsers_common.articlePostsRange(articleLoopUrls, maxArticlePostsCount):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articleLoopUrls)) + ") on " + articleLoopUrls[j], 2)

                # author
                articleDataDict["authors"].append(articleLoopAuthors[j])

                # description
                curArtDescChilds = parsers_common.stringify_index_children(articleLoopDescriptionsParents, j)
                curArtDescChilds = parsers_common.fixDrunkPost(curArtDescChilds)
                articleDataDict["descriptions"].append(curArtDescChilds)

                # datetime
                curArtPubDate = articleLoopPubDates[j]
                curArtPubDate = parsers_common.monthsToNumber(curArtPubDate)
                curArtPubDate = parsers_common.removeWeekDayTexts(curArtPubDate)

                if (curArtPubDate.find(".") > 0):
                    # timeformat magic from "Pühapäev 26. Mai 2019, 18:07:05" to datetime()
                    curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d. %m %Y, %H:%M:%S")
                elif (curArtPubDate.find(",") > 0):
                    # timeformat magic from "R Juun 26, 2019 8:07 pm" to datetime()
                    curArtPubDate = parsers_common.rawToDatetime(curArtPubDate[2:], "%m %d, %Y %I:%M %p")
                else:
                    # timeformat magic from "» 29 Dec 2017 13:46" to datetime()
                    curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "» %d %m %Y %H:%M")
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                articleDataDict["titles"].append(articlePreLoopTitles[i] + " @" + domain)

                # url
                articleDataDict["urls"].append(articleLoopUrls[j].split("&sid=")[0] + "#" + articleLoopUrls[j].split("#")[1])

            # remove unwanted content
            k = 0
            while (k < min(len(articleDataDict["urls"]), maxArticleCount)):
                rss_print.print_debug(__file__, "kontrollime kannet: " + str(k + 1) + ", kokku: " + str(len(articleDataDict["urls"])), 4)
                if (articleDataDict["descriptions"][k].find("jumal ") >= 0 or articleDataDict["descriptions"][k].find("Jumal ") >= 0):
                    articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
                else:
                    k += 1

    return articleDataDict
