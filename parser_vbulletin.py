#!/usr/bin/env python3

import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    maxArticleBodies = min(rss_config.MAX_ARTICLE_BODIES, 15)
    maxArticlePostsCount = round(rss_config.MAX_ARTICLE_BODIES / maxArticleBodies)  # set 0 for all posts

    articlesTitles = parsers_common.xpath_to_list(pageTree, '//li/div/div/div[@class="inner"]/h3/a/text()')
    articlesUrls = parsers_common.xpath_to_list(pageTree, '//li/div/div/div[@class="inner"]/h3/a/@href')

    if not articlesUrls:
        rss_print.print_debug(__file__, "ei leidnud teemade nimekirjast ühtegi aktiivset teemat", 0)

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlesUrls):
        # teemalehe sisu hankimine
        if (rss_config.GET_ARTICLE_BODIES is True and i < maxArticleBodies):
            articlesUrls[i] = articlesUrls[i].split("&sid=")[0]

            pageTree = parsers_common.get_article_tree(session, domain, articlesUrls[i] + "&start=100000", noCache=True)

            articlesPostsAuthors = parsers_common.xpath_to_list(pageTree, '//ol/li/div[@class="postdetails"]/div[@class="userinfo"]/div[@class="username_container"]/div[@class="popupmenu memberaction"]/a/strong/text()')
            articlesPostsPubDates = parsers_common.xpath_to_list(pageTree, '//ol/li/div[@class="posthead"]/span/span[@class="date"]/text()')
            articlesPostsPubTimes = parsers_common.xpath_to_list(pageTree, '//ol/li/div[@class="posthead"]/span/span[@class="date"]/span[@class="time"]/text()')
            articlesPostsUrls = parsers_common.xpath_to_list(pageTree, '//ol/li/div[@class="posthead"]/span[@class="nodecontrols"]/a/@href')
            articlesPostsDescriptions = parsers_common.xpath_to_list(pageTree, '//ol/li/div[2]/div[2]/div[1]/div/div/blockquote', parent=True)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlesPostsUrls, maxArticlePostsCount):
                # author
                curArtAuthor = articlesPostsAuthors[j]
                articleDataDict["authors"].append(curArtAuthor)

                # description
                curArtDesc = articlesPostsDescriptions[j]
                if "elfafoorum.ee" in domain:
                    curArtDesc = curArtDesc.replace('<img src="images/misc/quote_icon.png" alt="Tsitaat"> Esmalt postitatud', "")
                    curArtDesc = curArtDesc.replace('<img class="inlineimg" src="images/buttons2/viewpost-right.png" alt="Vaata postitust">', "")
                    curArtDesc = parsers_common.fix_quatation_tags(curArtDesc, '<div class="quote_container">', "</div>", "<blockquote>", "</blockquote>")
                curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
                articleDataDict["descriptions"].append(curArtDesc)

                # datetime
                curArtPubDate = articlesPostsPubDates[j] + articlesPostsPubTimes[j]
                curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "Eile", "%d-%m-%y", offSetDays=-1)
                curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "Täna", "%d-%m-%y", offSetDays=0)
                curArtPubDate = parsers_datetime.guess_datetime(curArtPubDate)
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                curArtTitle = parsers_common.title_at_domain(articlesTitles[i], domain)
                articleDataDict["titles"].append(curArtTitle)

                # url
                curArtUrl = articlesPostsUrls[j]
                curArtUrl = curArtUrl.split("&sid=")[0]
                if "#" not in curArtUrl:
                    rss_print.print_debug(__file__, "lisame lingi lõppu puuduva:" + "#" + articlesPostsUrls[j].split("#")[1], 0)
                    curArtUrl = curArtUrl + "#" + articlesPostsUrls[j].split("#")[1]
                articleDataDict["urls"].append(curArtUrl)

                rss_print.print_debug(__file__, "teema postitus nr. " + str(j + 1) + "/(" + str(len(articlesPostsUrls)) + ") on " + articlesPostsUrls[j], 2)

    # remove unwanted content
    dictBlacklist = ["jumal ", "Jumal "]
    dictCond = "in"
    dictField = "descriptions"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    return articleDataDict
