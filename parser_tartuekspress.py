#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="forum"][2]/ul/li/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="forum"][2]/ul/li/a/@href')

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        if (getArticleBodies is True) and (i < maxArticleCount):
            # load article into tree
            articleTree = parsers_common.getArticleData(domain, articleDataDict["urls"][i], False)

            # description
            curArtDescChilds = parsers_common.xpath_parent_to_single(articleTree, '//div[@id="content"]/div[@class="full_width"]')
            articleDataDict["descriptions"].append(curArtDescChilds)

            # author
            try:
                curArtAuthor = curArtDescChilds
                curArtAuthor = curArtAuthor.split('<i> Autor: <b>')[1]
                curArtAuthor = curArtAuthor.split('</b>')[0]
                articleDataDict["authors"].append(curArtAuthor)
            except Exception as e:
                rss_print.print_debug(__file__, "exception = " + str(e), 1)
                rss_print.print_debug(__file__, "ei leia autorit, leht on tuksis?", 0)

            # it's not possible to make two similar search on same dataset
            articleTree = parsers_common.getArticleData(domain, articleDataDict["urls"][i], False)

            # image
            curArtPubImage = parsers_common.xpath_to_single(articleTree, '//div[@id="content"]/div[@class="full_width"]/a/img[@class="thumb"]/@src')
            articleDataDict["images"].append(curArtPubImage)

            # timeformat magic from "13/12/2017 22:24:59" to to datetime()
            curArtPubDate = parsers_common.xpath_to_single(articleTree, '//div[@id="content"]/div[@class="full_width"]/p[*]/i/b[2]/text()')
            curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d/%m/%Y %H:%M:%S")
            articleDataDict["pubDates"].append(curArtPubDate)

    return articleDataDict
