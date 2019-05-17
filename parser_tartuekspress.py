#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Tartu Ekspressi RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


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
        fulltext.append(parsers_common.toPlaintext(rawtext))
    return ''.join(fulltext)


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod saidi kõigi uudiste nimekirja loomiseks
    """

    articleAuthors = []
    articleDescriptions = []
    articleImages = []
    articlePubDates = []
    articleTitles = parsers_common.xpath(pageTree, '//div[@class="forum"][2]/ul/li/a/text()')
    articleUrls = parsers_common.xpath(pageTree, '//div[@class="forum"][2]/ul/li/a/@href')

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        if (getArticleBodies is True):
            # load article into tree
            articleTree = parsers_common.getArticleData(domain, articleUrls[i], False)
            articleTreeBuf = parsers_common.getArticleData(domain, articleUrls[i], False)

            # description
            curArtDescParent = parsers_common.treeExtract(articleTree, '//div[@id="content"]/div[@class="full_width"]')   # as a parent
            curArtDescriptionsChilds = parsers_common.stringify_children(curArtDescParent)
            curArtDescriptionsChilds = curArtDescriptionsChilds.split('<a name="fb_share">')[0]
            articleDescriptions.append(curArtDescriptionsChilds)

            # author
            articleAuthors.append(curArtDescriptionsChilds.split('Autor:')[1].split('</b>')[0].split('<b>')[1])

            # it's not possible to make two similar search on same dataset
            articleTree = articleTreeBuf

            # image
            curArtPubImage = parsers_common.treeExtract(articleTree, '//div[@id="content"]/div[@class="full_width"]/a/img[@class="thumb"]/@src') or "/"
            articleImages.append(curArtPubImage)

            # timeformat magic from "13/12/2017 22:24:59" to to datetime()
            try:
                curArtPubDate = parsers_common.treeExtract(articleTree, '//div[@id="content"]/div[@class="full_width"]/p[*]/i/b[2]/text()')
                curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d/%m/%Y %H:%M:%S")
                articlePubDates.append(curArtPubDate)
            except Exception:
                rss_print.print_debug(__file__, "kellaaja hankimine ebaõnnestus! Liiga palju <p> elemente?")

    return {"articleAuthors": articleAuthors,
            "articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
            }
