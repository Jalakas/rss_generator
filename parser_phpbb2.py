#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    maxArticleBodies = min(maxArticleBodies, 15)
    maxArticlePostsCount = round(150 / maxArticleBodies)  # set 0 for all posts

    articlePreLoopTitles = parsers_common.xpath_to_list(pageTree, '//tr[@valign="middle"]/td[3]/a/text()')
    articlePreLoopUrls = parsers_common.xpath_to_list(pageTree, '//tr[@valign="middle"]/td[3]/a/@href')

    if not articlePreLoopUrls:
        rss_print.print_debug(__file__, "ei leidnud nimekirjast ühtegi aktiivset teemat", 0)

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlePreLoopUrls):
        if (articlePreLoopTitles[i] == "Merevägi ja rannakaitse"):
            rss_print.print_debug(__file__, "jätame vahele teema: 'Merevägi ja rannakaitse'", 1)
            continue

        # teemalehe sisu hankimine
        if (getArticleBodies is True and i < maxArticleBodies):
            articlePreLoopUrls[i] = articlePreLoopUrls[i].split("&sid=")[0]
            articlePostsTree = parsers_common.get_article_data(domain, articlePreLoopUrls[i] + "&start=20000", True)  # True teeb alati päringu

            articleLoopAuthors = parsers_common.xpath_to_list(articlePostsTree, '//tr/td/b[@class="postauthor"]/text()')
            articleLoopPubDates = parsers_common.xpath_to_list(articlePostsTree, '//tr/td[@class="gensmall"]/div[2]/text()')
            articleLoopUrls = parsers_common.xpath_to_list(articlePostsTree, '//tr/td[@class="gensmall"]/div[2]/a/@href')
            articleLoopDescriptionsParents = parsers_common.xpath_to_list(articlePostsTree, '//tr/td/div[@class="postbody"][1]', parent=True)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articleLoopUrls, maxArticlePostsCount):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articleLoopUrls)) + ") on " + articleLoopUrls[j], 2)

                # author
                articleDataDict["authors"].append(articleLoopAuthors[j])

                # description
                curArtDescChilds = parsers_common.stringify_index_children(articleLoopDescriptionsParents, j)
                curArtDescChilds = curArtDescChilds.replace("</blockquote><br>", "</blockquote>")
                curArtDescChilds = curArtDescChilds.replace("</blockquote></div>", "</blockquote>")
                curArtDescChilds = curArtDescChilds.replace("<div><blockquote>", "<blockquote>")
                curArtDescChilds = curArtDescChilds.replace("<div><b>Tsiteeri:</b></div>", "")
                curArtDescChilds = parsers_common.fix_drunk_post(curArtDescChilds)
                curArtDescChilds = parsers_common.format_tags(curArtDescChilds, '<div class="quotecontent">', "</div>", "<blockquote>", "</blockquote>")
                articleDataDict["descriptions"].append(curArtDescChilds)

                # datetime
                # timeformat magic from "03 mär, 2019 16:26" to datetime()
                curArtPubDate = parsers_common.months_to_int(articleLoopPubDates[j])
                curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d %m, %Y %H:%M")
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                articleDataDict["titles"].append(articlePreLoopTitles[i] + " @" + domain)

                # url
                articleDataDict["urls"].append(articleLoopUrls[j].split("&sid=")[0] + "#" + articleLoopUrls[j].split("#")[1])

    return articleDataDict
