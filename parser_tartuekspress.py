#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="forum"][2]/ul/li/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="forum"][2]/ul/li/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if (getArticleBodies is True and i < maxArticleBodies):
            # load article into tree
            articleTree = parsers_common.get_article_data(domain, articleDataDict["urls"][i], False)

            # description
            curArtDescChilds = parsers_common.xpath_to_single(articleTree, '//div[@id="content"]/div[@class="full_width"]', parent=True)
            articleDataDict["descriptions"].append(curArtDescChilds)

            # author
            try:
                curArtAuthor = curArtDescChilds
                curArtAuthor = curArtAuthor.split('<i> Autor: <b>')[1]
                curArtAuthor = curArtAuthor.split('</b>')[0]
                articleDataDict["authors"].append(curArtAuthor)
            except Exception as e:
                rss_print.print_debug(__file__, "ei leia autorit, leht on tuksis?", 0)
                rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

            # it's not possible to make two similar search on same dataset
            articleTree = parsers_common.get_article_data(domain, articleDataDict["urls"][i], False)

            # image
            curArtPubImage = parsers_common.xpath_to_single(articleTree, '//div[@id="content"]/div[@class="full_width"]/a/img[@class="thumb"]/@src')
            articleDataDict["images"].append(curArtPubImage)

            # timeformat magic from "13/12/2017 22:24:59" to to datetime()
            curArtPubDate = parsers_common.xpath_to_single(articleTree, '//div[@id="content"]/div[@class="full_width"]/p[*]/i/b[2]/text()')
            curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d/%m/%Y %H:%M:%S")
            articleDataDict["pubDates"].append(curArtPubDate)

    return articleDataDict
