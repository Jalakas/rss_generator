#!/usr/bin/env python3

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    maxArticleBodies = min(rss_config.MAX_ARTICLE_BODIES, 15)
    maxArticlePostsCount = round(200 / maxArticleBodies)  # set 0 for all posts

    articlesTitles = parsers_common.xpath_to_list(pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="title"]/a/@title')
    articlesUrls = parsers_common.xpath_to_list(pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="title"]/a/@href')

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlesUrls):
        if articlesTitles[i] == "Kalev Jaik võsafilosoofist majandusteadlane":
            rss_print.print_debug(__file__, "jätame vahele teema: 'Kalev Jaik võsafilosoofist majandusteadlane'", 1)
            continue

        # teemalehe sisu hankimine
        if (rss_config.GET_ARTICLE_BODIES is True and i < maxArticleBodies):
            articlesPostsTree = parsers_common.get_article_tree(session, domain, articlesUrls[i] + '?listEventId=jumpToPage&listEventParam=100&pagesOfMaxSize=true', noCache=True)

            articlesPostsAuthors = parsers_common.xpath_to_list(articlesPostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/p[@class="author"]/strong/a/text()')
            articlesPostsIds = parsers_common.xpath_to_list(articlesPostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/@href')
            articlesPostsPubDates = parsers_common.xpath_to_list(articlesPostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/node()')
            articlesPostsDescriptions = parsers_common.xpath_to_list(articlesPostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-content temporary-class"]', parent=True)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlesPostsIds, maxArticlePostsCount):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articlesPostsIds)) + ") on " + articlesPostsIds[j], 3)

                # generate articleDataDict["urls"] from articlesPostsIds
                articleDataDict["urls"].append(articlesUrls[i] + articlesPostsIds[j])

                # author
                articleDataDict["authors"].append(articlesPostsAuthors[j])

                # description
                curArtDesc = articlesPostsDescriptions[j]
                curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
                articleDataDict["descriptions"].append(curArtDesc)

                # timeformat magic from "15.01.2012 23:49" to datetime()
                curArtPubDate = articlesPostsPubDates[j]
                curArtPubDate = parsers_common.replace_string_with_timeformat(curArtPubDate, "Eile", "%d.%m.%Y", offSetDays=-1)
                curArtPubDate = parsers_common.add_missing_date_to_string(curArtPubDate, "%d.%m.%Y %H:%M", "%d.%m.%Y ")
                curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                articleDataDict["titles"].append(articlesTitles[i] + " @" + parsers_common.simplify_link(domain))

    return articleDataDict
