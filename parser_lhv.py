#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    LHV RSS-voo sisendite parsimine
"""

from datetime import datetime, timedelta
import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod foorumi kõigi postituste nimekirja loomiseks
    """

    maxArticleCount = 8
    articlePostsCount = round(100 / maxArticleCount)  # set 0 for all posts

    articleTitles = pageTree.xpath('//table[@class="grid zebra forum"]//tr/td[@class="title"]/a/@title')
    articleUrls = pageTree.xpath('//table[@class="grid zebra forum"]//tr/td[@class="title"]/a/@href')
    articleUrls = parsers_common.domainUrls(domain, articleUrls)

    articlePostsDescriptions = []
    articlePostsIds = []
    articlePostsImages = []
    articlePostsPubDates = []
    articlePostsTitles = []
    articlePostsUrls = []

    # teemade läbivaatamine
    for i in range(0, min(len(articleUrls), maxArticleCount)):
        if (articleUrls[i] == "https://fp.lhv.ee/forum/free/121915"):  # Kalev Jaik võsafilosoofist majandusteadlane
            rss_print.print_debug(__file__, 'jätame Jaiki filosoofia vahele', 0)
            i += 1

        # teemalehe sisu hankimine
        if (getArticleBodies is True):
            articlePostsTree = parsers_common.getArticleData(articleUrls[i] + '?listEventId=jumpToPage&listEventParam=100&pagesOfMaxSize=true', True)  # True teeb alati päringu

            articlePostsIdsRaw = articlePostsTree.xpath(
                '//ul/li/div[@class="col2"]/div/div/p[@class="permalink"]/a/@href')
            articlePostsPubDatesRaw = articlePostsTree.xpath(
                '//ul/li/div[@class="col2"]/div/div/p[@class="permalink"]/a/text()')
            articlePostsDescriptionsParents = articlePostsTree.xpath(
                '//ul/li/div[@class="col2"]/div[@class="forum-content temporary-class"]')

            rss_print.print_debug(__file__, 'xpath parsimisel ' + str(len(articlePostsIdsRaw)) + " leid(u)", 1)

            # postituste läbivaatamine
            for j in range(max(0, len(articlePostsIdsRaw) - articlePostsCount), len(articlePostsIdsRaw)):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articlePostsIdsRaw)) + ") on " + articlePostsIdsRaw[j], 2)

                # generate articlePostsUrls from articlePostsId
                articlePostsUrls.append(articleUrls[i] + articlePostsIdsRaw[j])

                # pärast lingi koostamist lühendame id koodi
                articlePostsIds.append(articlePostsIdsRaw[j].split("=")[-1])

                # description
                curArtDescriptionsChilds = parsers_common.stringify_children(articlePostsDescriptionsParents[j])
                articlePostsDescriptions.append(curArtDescriptionsChilds)

                # title
                articlePostsTitles.append(articleTitles[i] + " @" + domain)

                # timeformat magic from "15.01.2012 23:49" to datetime()
                curArtPubDate = articlePostsPubDatesRaw[j]
                curArtPubDate = curArtPubDate.strip()
                curArtPubDate = curArtPubDate.replace('Eile', (datetime.now() - timedelta(days=1)).strftime('%d.%m.%Y'))
                if len(curArtPubDate) < len("%d.%m.%Y %H:%M"):
                    curArtPubDate = datetime.now().strftime('%d.%m.%Y') + ' ' + curArtPubDate
                    rss_print.print_debug(__file__, "lisasime tänasele kellaajale kuupäeva: " + curArtPubDate, 3)
                curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y %H:%M")
                articlePostsPubDates.append(curArtPubDate)

    return {"articleDescriptions": articlePostsDescriptions,
            "articleIds": articlePostsIds,
            "articleImages": articlePostsImages,
            "articlePubDates": articlePostsPubDates,
            "articleTitles": articlePostsTitles,
            "articleUrls": articlePostsUrls,
           }
