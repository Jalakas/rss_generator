#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    maxArticleBodies = min(maxArticleBodies, 15)
    maxArticlePostsCount = round(150 / maxArticleBodies)  # set 0 for all posts

    articlePreLoopTitles = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[1]/text()')
    articlePreLoopUrls = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[1]/@href')

    if not articlePreLoopUrls:
        if (domain == "http://arutelud.com"):
            rss_print.print_debug(__file__, "aktiivseid teemasid ei leitud, arutelude foorumis külastame mammutteemat", 0)
            articlePreLoopTitles.append("Arutelud")
            articlePreLoopUrls.append("http://arutelud.com/viewtopic.php?f=3&t=4&sd=d&sk=t&st=7")
        else:
            rss_print.print_debug(__file__, "aktiivseid teemasid ei leitud", 0)

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlePreLoopUrls):
        # teemalehe sisu hankimine
        if (getArticleBodies is True and i < maxArticleBodies):
            articlePreLoopUrls[i] = articlePreLoopUrls[i].split("&sid=")[0]
            articlePostsTree = parsers_common.get_article_data(domain, articlePreLoopUrls[i] + "&start=100000", True)  # True teeb alati päringu

            articleLoopAuthors = parsers_common.xpath_to_list(articlePostsTree, '//p[@class="author"]//strong//text()')
            articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//p[@class="author"]/text()[1]')
            articleLoopUrls = parsers_common.xpath_to_list(articlePostsTree, '//p[@class="author"]/a/@href')
            articleLoopDescriptionsParents = parsers_common.xpath_to_list(articlePostsTree, '//div[@class="content"]', parent=True)

            if articleLoopUrls:
                if not articleLoopPubDates:
                    rss_print.print_debug(__file__, "ei suutnud hankida ühtegi aega", 0)
                else:
                    if (len(str(articleLoopPubDates[0]).strip()) < 5):
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articleLoopPubDates[0] + "', proovime alternatiivi...", 1)
                        articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//p[@class="author"]/text()[2]')
                    if (len(str(articleLoopPubDates[0]).strip()) < 5):
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articleLoopPubDates[0] + "'", 0)
                    else:
                        rss_print.print_debug(__file__, "hangitud aeg[0]: '" + articleLoopPubDates[0] + "'", 4)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articleLoopUrls, maxArticlePostsCount):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articleLoopUrls)) + ") on " + articleLoopUrls[j], 2)

                # author
                articleDataDict["authors"].append(articleLoopAuthors[j])

                # description
                curArtDescChilds = parsers_common.stringify_index_children(articleLoopDescriptionsParents, j)
                curArtDescChilds = parsers_common.fix_drunk_post(curArtDescChilds)
                articleDataDict["descriptions"].append(curArtDescChilds)

                # datetime
                curArtPubDate = articleLoopPubDates[j]
                curArtPubDate = parsers_common.months_to_int(curArtPubDate)
                curArtPubDate = parsers_common.remove_weekday_strings(curArtPubDate)

                if (curArtPubDate.find(".") > 0):
                    # timeformat magic from "Pühapäev 26. Mai 2019, 18:07:05" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d. %m %Y, %H:%M:%S")
                elif (curArtPubDate.find(",") > 0):
                    # timeformat magic from "R Juun 26, 2019 8:07 pm" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate[2:], "%m %d, %Y %I:%M %p")
                else:
                    # timeformat magic from "» 29 Dec 2017 13:46" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "» %d %m %Y %H:%M")
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                articleDataDict["titles"].append(articlePreLoopTitles[i] + " @" + domain)

                # url
                articleDataDict["urls"].append(articleLoopUrls[j].split("&sid=")[0] + "#" + articleLoopUrls[j].split("#")[1])

            # remove unwanted content
            k = 0
            while (k < len(articleDataDict["urls"])):
                rss_print.print_debug(__file__, "kontrollime kannet(" + str(k + 1) + "/" + str(len(articleDataDict["urls"])) + "): " + articleDataDict["titles"][k], 2)
                if (
                        articleDataDict["descriptions"][k].find("jumal ") >= 0 or
                        articleDataDict["descriptions"][k].find("Jumal ") >= 0
                ):
                    articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
                else:
                    k += 1

    return articleDataDict
