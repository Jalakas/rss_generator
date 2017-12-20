#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Tartu Ekspressi RSS-voo sisendite parsimine
"""

import makereq
import parsers_common


def extractArticleBody(articleTree):
    """
    Artikli tervikteksti saamiseks
    """
    body = articleTree.xpath('//div[@class="full_width"]/p')
    fulltext = []
    for elem in body:
        rawtext = elem.text_content()
        try:
            rawtext = rawtext[:rawtext.index('Tweet\n')]
        except ValueError:
            None
        fulltext.append(rawtext)
    return ''.join(fulltext)


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod uudistesaidi kõigi uudiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = []
    articlePubDates = []
    articleTitles = pageTree.xpath('//div[@class="forum"][2]/ul/li/a/text()')
    articleUrls = pageTree.xpath('//div[@class="forum"][2]/ul/li/a/@href')
    articleUrls = [domain + elem for elem in articleUrls]

    get_article_bodies = True

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl[articleUrl.index('&id=') + 4:articleUrl.index('&', articleUrl.index('&id=') + 4)])

        if (get_article_bodies is True and i < maxPageURLstoVisit):
            # load article into tree
            articleTree = makereq.getArticleData(articleUrl)

            # descriptions
            # articleDescriptions.append(parsers_common.treeExtract(articleTree, '//div[@id="content"]/div[@class="full_width"]/p[1]/strong/text()'))  # esimene peatükk pole alati strong
            articleDescriptionsParent = parsers_common.treeExtract(articleTree, '//div[@id="content"]/div[@class="full_width"]/p[1]')   # as a parent
            articleDescriptionsChilds = parsers_common.stringify_children(articleDescriptionsParent)
            articleDescriptions.append(articleDescriptionsChilds)

            # images
            curArtPubImage = parsers_common.treeExtract(articleTree, '//div[@id="content"]/div[@class="full_width"]/a/img[@class="thumb"]/@src')
            articleImages.append(curArtPubImage)

            # timeformat magic from "13/12/2017 22:24:59" to to datetime()
            curArtPubDate = parsers_common.treeExtract(articleTree, '//div[@id="content"]/div[@class="full_width"]/p[*]/i/b[2]/text()')
            curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d/%m/%Y %H:%M:%S")
            articlePubDates.append(curArtPubDate)

    articleImages = [domain + elem for elem in articleImages]

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
            }
