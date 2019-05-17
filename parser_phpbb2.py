#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod foorumi kõigi postituste nimekirja loomiseks
    """

    maxArticleCount = 15
    articlePostsCount = round(150 / maxArticleCount)  # set 0 for all posts

    articleTitles = parsers_common.xpath(pageTree, '//tr[@valign="middle"]/td[3]/a/text()')
    articleUrls = parsers_common.xpath(pageTree, '//tr[@valign="middle"]/td[3]/a/@href')

    articlePostsAuthors = []
    articlePostsDescriptions = []
    articlePostsImages = []
    articlePostsPubDates = []
    articlePostsTitles = []
    articlePostsUrls = []

    # teemade läbivaatamine
    for i in range(0, min(len(articleUrls), maxArticleCount)):

        # teemalehe sisu hankimine
        if (getArticleBodies is True):
            articleUrls[i] = articleUrls[i].split("&sid=")[0]
            articlePostsTree = parsers_common.getArticleData(domain, articleUrls[i] + "&start=20000", True)  # True teeb alati päringu

            articleLoopAuthors = parsers_common.xpath_devel(articlePostsTree, '//tr/td/b[@class="postauthor"]/text()')
            articleLoopIds = parsers_common.xpath_devel(articlePostsTree, '//tr/td[@class="gensmall"]/div[2]/a/@href')
            articleLoopPubDates = parsers_common.xpath_devel(articlePostsTree, '//tr/td[@class="gensmall"]/div[2]/text()')
            articleLoopDescriptionsParents = parsers_common.xpath_devel(articlePostsTree, '//tr/td/div[@class="postbody"][1]')  # as a parent

            rss_print.print_debug(__file__, 'xpath parsimisel ' + str(len(articleLoopIds)) + " leid(u)", 1)

            # postituste läbivaatamine
            for j in range(max(0, len(articleLoopIds) - articlePostsCount), len(articleLoopIds)):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articleLoopIds)) + ") on " + articleLoopIds[j], 2)

                # generate articlePostsUrls from articlePostsIds
                articlePostsUrls.append(articleLoopIds[j].split("&sid=")[0] + "#" + articleLoopIds[j].split("#")[1])

                # author
                articlePostsAuthors.append(articleLoopAuthors[j])

                # description
                curArtDescriptionsChilds = parsers_common.stringify_children(articleLoopDescriptionsParents[j]) + " "
                curArtDescriptionsChilds = parsers_common.fixDrunkPost(curArtDescriptionsChilds)
                articlePostsDescriptions.append(curArtDescriptionsChilds)

                # timeformat magic from "03 mär, 2019 16:26" to datetime()
                curArtPubDate = articleLoopPubDates[j]
                curArtPubDate = curArtPubDate.strip()
                curArtPubDate = parsers_common.shortMonthsToNumber(curArtPubDate)
                curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d %m, %Y %H:%M")
                articlePostsPubDates.append(curArtPubDate)

                # title
                articlePostsTitles.append(articleTitles[i] + " @" + domain)

    return {"articleAuthors": articlePostsAuthors,
            "articleDescriptions": articlePostsDescriptions,
            "articleImages": articlePostsImages,
            "articlePubDates": articlePostsPubDates,
            "articleTitles": articlePostsTitles,
            "articleUrls": articlePostsUrls,
           }
