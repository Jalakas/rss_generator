#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    LHV RSS-voo sisendite parsimine
"""

from datetime import datetime, timedelta
import makereq
import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod foorumi kõigi postituste nimekirja loomiseks
    """

    domain = 'https://fp.lhv.ee'

    # articleDescriptions = []
    # articleIds = []
    # articleImages = []
    # articlePubDates = pageTree.xpath('//table[@class="grid zebra forum"]//tr/td[@class="meta"][3]/text()')
    articleTitles = pageTree.xpath('//table[@class="grid zebra forum"]//tr/td[@class="title"]/a/@title')
    articleUrls = pageTree.xpath('//table[@class="grid zebra forum"]//tr/td[@class="title"]/a/@href')
    articleUrls = parsers_common.domainUrls(domain, articleUrls)

    get_article_bodies = True
    maxPageURLstoVisit = 1

    # teemade läbivaatamine
    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i] + '?pagesOfMaxSize=true'
        articleTitle = articleTitles[i]

        # teemalehe hankimine
        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articlePostTree = makereq.getArticleData(articleUrl)

            articlePostDescriptions = []
            articlePostIds = articlePostTree.xpath('//ul/li/div[@class="col2"]//p[@class="permalink"]/a/@href')
            articlePostImages = []
            articlePostPubDates = articlePostTree.xpath('//ul/li/div[@class="col2"]//p[@class="permalink"]/a/text()')
            articlePostTitles = []
            articlePostUrls = []

            articlePostDescriptionsParents = articlePostTree.xpath('//ul/li/div[@class="col2"]/div[@class="forum-content temporary-class"]')

            # postide läbivaatamine
            for j in range(0, len(articlePostIds)):

                # generate articlePostUrls from articlePostId
                articlePostUrls.append(articleUrl + articlePostIds[j])

                # pärast lingi koostamist lühendame id koodi
                articlePostIds[j] = articlePostIds[j].split("=")[-1]

                # description
                curArtDescChilds = parsers_common.stringify_children(articlePostDescriptionsParents[j])
                articlePostDescriptions.append(curArtDescChilds)

                # title
                articlePostTitles.append(articleTitle + " @" + domain)

                yesterday = datetime.now() - timedelta(days=1)
                # timeformat magic from "15.01.2012 23:49" to datetime()
                curArtPubDate = articlePostPubDates[j]
                curArtPubDate = curArtPubDate.strip()
                curArtPubDate = curArtPubDate.replace('Eile', yesterday.strftime('%d.%m.%Y'))
                if len(curArtPubDate) > 5:
                    curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y %H:%M")
                else:
                    curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%H:%M")
                articlePostPubDates[j] = curArtPubDate

    return {"articleDescriptions": articlePostDescriptions,
            "articleIds": articlePostIds,
            "articleImages": articlePostImages,
            "articlePubDates": articlePostPubDates,
            "articleTitles": articlePostTitles,
            "articleUrls": articlePostUrls,
           }
