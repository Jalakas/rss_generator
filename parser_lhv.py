#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    maxArticleBodies = min(maxArticleBodies, 15)
    maxArticlePostsCount = round(200 / maxArticleBodies)  # set 0 for all posts

    articlePreLoopTitles = parsers_common.xpath_to_list(pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="title"]/a/@title')
    articlePreLoopUrls = parsers_common.xpath_to_list(pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="title"]/a/@href')

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlePreLoopUrls):
        if (articlePreLoopUrls[i] == "/forum/free/121915"):  # Kalev Jaik võsafilosoofist majandusteadlane
            rss_print.print_debug(__file__, "jätame vahele teema: 'Jaiki filosoofia'", 1)
            continue

        # teemalehe sisu hankimine
        if (getArticleBodies is True and i < maxArticleBodies):
            articlePostsTree = parsers_common.get_article_data(domain, articlePreLoopUrls[i] + '?listEventId=jumpToPage&listEventParam=100&pagesOfMaxSize=true', True)  # True teeb alati päringu

            articleDataDict["authors"] = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/p[@class="author"]/strong/a/text()')

            articleLoopAuthors = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/p[@class="author"]/strong/a/text()')
            articleLoopIds = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/@href')
            articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/node()')
            articleLoopDescriptionsParents = parsers_common.xpath_to_list(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-content temporary-class"]', parent=True)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articleLoopIds, maxArticlePostsCount):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articleLoopIds)) + ") on " + articleLoopIds[j], 3)

                # generate articleDataDict["urls"] from articlePostsIds
                articleDataDict["urls"].append(articlePreLoopUrls[i] + articleLoopIds[j])

                # author
                articleDataDict["authors"].append(articleLoopAuthors[j])

                # description
                curArtDescChilds = parsers_common.stringify_index_children(articleLoopDescriptionsParents, j)
                curArtDescChilds = parsers_common.fix_drunk_post(curArtDescChilds)
                articleDataDict["descriptions"].append(curArtDescChilds)

                # timeformat magic from "15.01.2012 23:49" to datetime()
                curArtPubDate = articleLoopPubDates[j]
                curArtPubDate = curArtPubDate.strip()
                curArtPubDate = parsers_common.replace_string_with_timeformat(curArtPubDate, "Eile", "%d.%m.%Y", offSetDays=-1)
                if len(curArtPubDate) < len("%d.%m.%Y %H:%M"):
                    curArtPubDate = parsers_common.add_to_time_string(curArtPubDate, "%d.%m.%Y ")
                    rss_print.print_debug(__file__, "lisasime kuupäevale 'kuupäeva' osa: " + curArtPubDate, 3)
                curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                articleDataDict["titles"].append(articlePreLoopTitles[i] + " @" + domain)

    return articleDataDict
