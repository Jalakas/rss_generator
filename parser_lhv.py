#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, session):

    maxArticleBodies = min(rss_config.MAX_ARTICLE_BODIES, 15)
    maxArticlePostsCount = round(200 / maxArticleBodies)  # set 0 for all posts

    articlePreLoopTitles = parsers_common.xpath_to_list(pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="title"]/a/@title')
    articlePreLoopUrls = parsers_common.xpath_to_list(pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="title"]/a/@href')

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlePreLoopUrls):
        if (articlePreLoopUrls[i] == "/forum/free/121915"):  # Kalev Jaik võsafilosoofist majandusteadlane
            rss_print.print_debug(__file__, "jätame vahele teema: 'Jaiki filosoofia'", 1)
            continue

        # teemalehe sisu hankimine
        if (rss_config.GET_ARTICLE_BODIES is True and i < maxArticleBodies):
            articlePostsTree = parsers_common.get_article_data(session, domain, articlePreLoopUrls[i] + '?listEventId=jumpToPage&listEventParam=100&pagesOfMaxSize=true', mainPage=True)

            articleDataDict["authors"] = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/p[@class="author"]/strong/a/text()')

            articleLoopAuthors = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/p[@class="author"]/strong/a/text()')
            articleLoopIds = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/@href')
            articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/node()')
            articleLoopDescriptions = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-content temporary-class"]', parent=True)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articleLoopIds, maxArticlePostsCount):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articleLoopIds)) + ") on " + articleLoopIds[j], 3)

                # generate articleDataDict["urls"] from articlePostsIds
                articleDataDict["urls"].append(articlePreLoopUrls[i] + articleLoopIds[j])

                # author
                articleDataDict["authors"].append(articleLoopAuthors[j])

                # description
                curArtDesc = articleLoopDescriptions[j]
                curArtDesc = parsers_common.rstrip_string(curArtDesc, "<br>")
                curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
                articleDataDict["descriptions"].append(curArtDesc)

                # timeformat magic from "15.01.2012 23:49" to datetime()
                curArtPubDate = articleLoopPubDates[j]
                curArtPubDate = parsers_common.replace_string_with_timeformat(curArtPubDate, "Eile", "%d.%m.%Y", offSetDays=-1)
                if len(curArtPubDate) < len("%d.%m.%Y %H:%M"):
                    curArtPubDate = parsers_common.add_to_time_string(curArtPubDate, "%d.%m.%Y ")
                    rss_print.print_debug(__file__, "lisasime kuupäevale 'kuupäeva' osa: " + curArtPubDate, 3)
                curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                articleDataDict["titles"].append(articlePreLoopTitles[i] + " @" + domain)

    return articleDataDict
