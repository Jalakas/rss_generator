#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, session):

    maxArticleBodies = min(rss_config.MAX_ARTICLE_BODIES, 15)
    maxArticlePostsCount = round(150 / maxArticleBodies)  # set 0 for all posts

    if (domain.find("militaar.net") > -1):
        articlePreLoopTitles = parsers_common.xpath_to_list(pageTree, '//tr[@valign="middle"]/td[3]/a/text()')
        articlePreLoopUrls = parsers_common.xpath_to_list(pageTree, '//tr[@valign="middle"]/td[3]/a/@href')
    else:
        articlePreLoopTitles = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[1]/text()')
        articlePreLoopUrls = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[1]/@href')

    if not articlePreLoopUrls:
        if (domain.find("arutelud.com") > -1):
            rss_print.print_debug(__file__, "aktiivseid teemasid ei leitud, arutelude foorumis külastame mammutteemat", 0)
            articlePreLoopTitles.append("Arutelud")
            articlePreLoopUrls.append("http://arutelud.com/viewtopic.php?f=3&t=4&sd=d&sk=t&st=7")
        else:
            rss_print.print_debug(__file__, "ei leidnud teemade nimekirjast ühtegi aktiivset teemat", 0)

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlePreLoopUrls):
        if (articlePreLoopTitles[i] == "Merevägi ja rannakaitse"):
            rss_print.print_debug(__file__, "jätame vahele teema: 'Merevägi ja rannakaitse'", 1)
            continue

        # teemalehe sisu hankimine
        if (rss_config.GET_ARTICLE_BODIES is True and i < maxArticleBodies):
            articlePreLoopUrls[i] = articlePreLoopUrls[i].split("&sid=")[0]

            articlePostsTree = parsers_common.get_article_data(session, domain, articlePreLoopUrls[i] + "&start=100000", mainPage=True)

            if (domain.find("militaar.net") > -1):
                articleLoopAuthors = parsers_common.xpath_to_list(articlePostsTree, '//tr/td/b[@class="postauthor"]/text()')
                articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//tr/td[@class="gensmall"]/div[2]/text()')
                articleLoopUrls = parsers_common.xpath_to_list(articlePostsTree, '//tr/td[@class="gensmall"]/div[2]/a/@href')
                articleLoopDescriptions = parsers_common.xpath_to_list(articlePostsTree, '//tr/td/div[@class="postbody"][1]', parent=True)
            else:
                articleLoopAuthors = parsers_common.xpath_to_list(articlePostsTree, '//p[@class="author"]//strong//text()')
                articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//p[@class="author"]/text()[1]')
                articleLoopUrls = parsers_common.xpath_to_list(articlePostsTree, '//p[@class="author"]/a/@href')
                articleLoopDescriptions = parsers_common.xpath_to_list(articlePostsTree, '//div[@class="content"]', parent=True)

            if articleLoopUrls:
                if not articleLoopPubDates:
                    rss_print.print_debug(__file__, "ei suutnud hankida ühtegi aega", 0)
                else:
                    if (len(str(articleLoopPubDates[0])) < 5):
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articleLoopPubDates[0] + "', proovime alternatiivi...", 1)
                        articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//p[@class="author"]/text()[2]')
                    if (len(str(articleLoopPubDates[0])) < 5):
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articleLoopPubDates[0] + "'", 0)
                    else:
                        rss_print.print_debug(__file__, "hangitud aeg[0]: '" + articleLoopPubDates[0] + "'", 4)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articleLoopUrls, maxArticlePostsCount):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articleLoopUrls)) + ") on " + articleLoopUrls[j], 2)

                # author
                articleDataDict["authors"].append(articleLoopAuthors[j])

                # description
                curArtDesc = articleLoopDescriptions[j]
                curArtDesc = curArtDesc.replace("</blockquote><br>", "</blockquote>")
                curArtDesc = curArtDesc.replace("</blockquote></div>", "</blockquote>")
                curArtDesc = curArtDesc.replace("<div><blockquote>", "<blockquote>")
                curArtDesc = curArtDesc.replace("<div><b>Tsiteeri:</b></div>", "")
                curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
                curArtDesc = parsers_common.format_tags(curArtDesc, '<div class="quotecontent">', "</div>", "<blockquote>", "</blockquote>")
                articleDataDict["descriptions"].append(curArtDesc)

                # datetime
                curArtPubDate = articleLoopPubDates[j]
                curArtPubDate = parsers_common.months_to_int(curArtPubDate)
                curArtPubDate = parsers_common.remove_weekday_strings(curArtPubDate)

                if (curArtPubDate.find(".") >= 0):
                    # timeformat magic from "Pühapäev 26. Mai 2019, 18:07:05" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d. %m %Y, %H:%M:%S")
                elif (curArtPubDate.find("am") >= 0 or curArtPubDate.find("pm") >= 0):
                    # timeformat magic from "R Juun 26, 2019 8:07 pm" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate[2:], "%m %d, %Y %I:%M %p")
                elif (curArtPubDate.find("»") >= 0):
                    # timeformat magic from "» 29 Dec 2017 13:46" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "» %d %m %Y %H:%M")
                else:
                    # timeformat magic from "03 mär, 2019 16:26" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d %m, %Y %H:%M")
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                articleDataDict["titles"].append(articlePreLoopTitles[i] + " @" + domain)

                # url
                curArtUrl = articleLoopUrls[j]
                curArtUrl = curArtUrl.split("&sid=")[0]
                if (curArtUrl.find("#") < 0):
                    rss_print.print_debug(__file__, "lisame lingi lõppu puuduva:" + "#" + articleLoopUrls[j].split("#")[1], 0)
                    curArtUrl = curArtUrl + "#" + articleLoopUrls[j].split("#")[1]
                articleDataDict["urls"].append(curArtUrl)

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
