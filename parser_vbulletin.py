#!/usr/bin/env python3

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    maxArticleBodies = min(rss_config.MAX_ARTICLE_BODIES, 15)
    maxArticlePostsCount = round(200 / maxArticleBodies)  # set 0 for all posts

    articlesTitles = parsers_common.xpath_to_list(pageTree, '//li/div/div/div[@class="inner"]/h3/a/text()')
    articlesUrls = parsers_common.xpath_to_list(pageTree, '//li/div/div/div[@class="inner"]/h3/a/@href')

    if not articlesUrls:
        rss_print.print_debug(__file__, "ei leidnud teemade nimekirjast ühtegi aktiivset teemat", 0)

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlesUrls):
        # teemalehe sisu hankimine
        if (rss_config.GET_ARTICLE_BODIES is True and i < maxArticleBodies):
            articlesUrls[i] = articlesUrls[i].split("&sid=")[0]

            articlesPostsTree = parsers_common.get_article_tree(session, domain, articlesUrls[i] + "&start=100000", noCache=True)

            articlesPostsAuthors = parsers_common.xpath_to_list(articlesPostsTree, '//ol/li/div[@class="postdetails"]/div[@class="userinfo"]/div[@class="username_container"]/div[@class="popupmenu memberaction"]/a/strong/text()')
            articlesPostsPubDates = parsers_common.xpath_to_list(articlesPostsTree, '//ol/li/div[@class="posthead"]/span/span[@class="date"]/text()')
            articlesPostsPubTimes = parsers_common.xpath_to_list(articlesPostsTree, '//ol/li/div[@class="posthead"]/span/span[@class="date"]/span[@class="time"]/text()')
            articlesPostsUrls = parsers_common.xpath_to_list(articlesPostsTree, '//ol/li/div[@class="posthead"]/span[@class="nodecontrols"]/a/@href')
            articlesPostsDescriptions = parsers_common.xpath_to_list(articlesPostsTree, '//ol/li/div[2]/div[2]/div[1]/div/div/blockquote', parent=True)

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
                curArtDesc = curArtDesc.replace("/threads/images/", "/images/")  # elfa tsitaadi alguse pildilingid on vigased
                curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
                curArtDesc = parsers_common.format_tags(curArtDesc, '<div class="quotecontent">', "</div>", "<blockquote>", "</blockquote>")
                articleDataDict["descriptions"].append(curArtDesc)

                # datetime
                curArtPubDate = articlesPostsPubDates[j] + articlesPostsPubTimes[j]
                curArtPubDate = parsers_common.replace_string_with_timeformat(curArtPubDate, "Eile", "%d-%m-%y", offSetDays=-1)
                curArtPubDate = parsers_common.replace_string_with_timeformat(curArtPubDate, "Täna", "%d-%m-%y", offSetDays=0)

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
