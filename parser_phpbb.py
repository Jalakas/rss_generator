#!/usr/bin/env python3

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    maxArticleBodies = min(rss_config.MAX_ARTICLE_BODIES, 15)
    maxArticlePostsCount = round(200 / maxArticleBodies)  # set 0 for all posts

    if (domain.find("militaar.net") >= 0):
        articlesTitles = parsers_common.xpath_to_list(pageTree, '//tr[@valign="middle"]/td[3]/a/text()')
        articlesUrls = parsers_common.xpath_to_list(pageTree, '//tr[@valign="middle"]/td[3]/a/@href')
    else:
        articlesTitles = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[1]/text()')
        articlesUrls = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[1]/@href')

    if not articlesUrls:
        if (domain.find("arutelud.com") >= 0):
            rss_print.print_debug(__file__, "aktiivseid teemasid ei leitud, arutelude foorumis külastame mammutteemat", 0)
            articlesTitles.append("Arutelud")
            articlesUrls.append("http://arutelud.com/viewtopic.php?f=3&t=4&sd=d&sk=t&st=7")
        else:
            rss_print.print_debug(__file__, "ei leidnud teemade nimekirjast ühtegi aktiivset teemat", 0)

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlesUrls):
        if (articlesTitles[i] == "Merevägi ja rannakaitse"):
            rss_print.print_debug(__file__, "jätame vahele teema: 'Merevägi ja rannakaitse'", 1)
            continue

        # teemalehe sisu hankimine
        if (rss_config.GET_ARTICLE_BODIES is True and i < maxArticleBodies):
            articlesUrls[i] = articlesUrls[i].split("&sid=")[0]
            articlesPostsTree = parsers_common.get_article_tree(session, domain, articlesUrls[i] + "&start=100000", noCache=True)

            if (domain.find("militaar.net") >= 0):
                articlesPostsAuthors = parsers_common.xpath_to_list(articlesPostsTree, '//tr/td/b[@class="postauthor"]/text()')
                articlesPostsPubDates = parsers_common.xpath_to_list(articlesPostsTree, '//tr/td[@class="gensmall"]/div[2]/text()')
                articlesPostsUrls = parsers_common.xpath_to_list(articlesPostsTree, '//tr/td[@class="gensmall"]/div[2]/a/@href')
                articlesPostsDescriptions = parsers_common.xpath_to_list(articlesPostsTree, '//tr/td/div[@class="postbody"][1]', parent=True)
            else:
                articlesPostsAuthors = parsers_common.xpath_to_list(articlesPostsTree, '//p[@class="author"]//strong//text()')
                articlesPostsPubDates = parsers_common.xpath_to_list(articlesPostsTree, '//p[@class="author"]/text()[1]')
                articlesPostsUrls = parsers_common.xpath_to_list(articlesPostsTree, '//p[@class="author"]/a/@href')
                articlesPostsDescriptions = parsers_common.xpath_to_list(articlesPostsTree, '//div[@class="content"]', parent=True)

            if articlesPostsUrls:
                if not articlesPostsPubDates:
                    rss_print.print_debug(__file__, "ei suutnud hankida ühtegi aega", 0)
                else:
                    if (len(str(articlesPostsPubDates[0])) < 5):
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articlesPostsPubDates[0] + "', proovime alternatiivi...", 1)
                        articlesPostsPubDates = parsers_common.xpath_to_list(articlesPostsTree, '//p[@class="author"]/text()[2]')
                    if (len(str(articlesPostsPubDates[0])) < 5):
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articlesPostsPubDates[0] + "'", 0)
                    else:
                        rss_print.print_debug(__file__, "hangitud aeg[0]: '" + articlesPostsPubDates[0] + "'", 4)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlesPostsUrls, maxArticlePostsCount):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articlesPostsUrls)) + ") on " + articlesPostsUrls[j], 2)

                # author
                articleDataDict["authors"].append(articlesPostsAuthors[j])

                # description
                curArtDesc = articlesPostsDescriptions[j]
                curArtDesc = curArtDesc.replace("</blockquote><br>", "</blockquote>")
                curArtDesc = curArtDesc.replace("</blockquote></div>", "</blockquote>")
                curArtDesc = curArtDesc.replace("<div><blockquote>", "<blockquote>")
                curArtDesc = curArtDesc.replace("<div><b>Tsiteeri:</b></div>", "")
                curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
                curArtDesc = parsers_common.format_tags(curArtDesc, '<div class="quotecontent">', "</div>", "<blockquote>", "</blockquote>")
                articleDataDict["descriptions"].append(curArtDesc)

                # datetime
                curArtPubDate = articlesPostsPubDates[j]
                curArtPubDate = parsers_common.months_to_int(curArtPubDate)
                curArtPubDate = parsers_common.remove_weekday_strings(curArtPubDate)

                if curArtPubDate.find("-") >= 0:
                    # timeformat magic from "21-11-16, 04:11" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d-%m-%y,%H:%M")
                elif curArtPubDate.find(".") >= 0:
                    # timeformat magic from "Pühapäev 26. Mai 2019, 18:07:05" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d. %m %Y, %H:%M:%S")
                elif (curArtPubDate.find("am") >= 0 or curArtPubDate.find("pm") >= 0):
                    # timeformat magic from "R Juun 26, 2019 8:07 pm" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate[2:], "%m %d, %Y %I:%M %p")
                elif curArtPubDate.find("»") >= 0:
                    # timeformat magic from "» 29 Dec 2017 13:46" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "» %d %m %Y %H:%M")
                else:
                    # timeformat magic from "03 mär, 2019 16:26" to datetime()
                    curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d %m, %Y %H:%M")
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                articleDataDict["titles"].append(articlesTitles[i] + " @" + parsers_common.simplify_link(domain))

                # url
                curArtUrl = articlesPostsUrls[j]
                curArtUrl = curArtUrl.split("&sid=")[0]
                if curArtUrl.find("#") < 0:
                    rss_print.print_debug(__file__, "lisame lingi lõppu puuduva:" + "#" + articlesPostsUrls[j].split("#")[1], 0)
                    curArtUrl = curArtUrl + "#" + articlesPostsUrls[j].split("#")[1]
                articleDataDict["urls"].append(curArtUrl)

    # remove unwanted content
    dictBlacklist = ["jumal ", "Jumal "]
    dictCond = "in"
    dictField = "descriptions"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    return articleDataDict
