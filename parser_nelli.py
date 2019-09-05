#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-cnt"]/div[@class="sb-article-prolog"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-image"]/@style')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-cnt"]/div[@class="sb-article-title"]/h3/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if (getArticleBodies is True and i < maxArticleBodies):
            # load article into tree
            articleTree = parsers_common.get_article_data(domain, articleDataDict["urls"][i], False)

            # author
            curArtAuthor = parsers_common.xpath_to_single(articleTree, '//div[@class="sg-article-details"]/div[@class="author"]/text()')
            articleDataDict["authors"].append(curArtAuthor)

            # timeformat magic from "18.08.2019 21:35" to datetime()
            curArtPubDate = parsers_common.xpath_to_single(articleTree, '//div[@class="sg-article-details"]/div[@class="date"]/text()')
            curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")
            articleDataDict["pubDates"].append(curArtPubDate)

            # description
            curArtDescChilds = parsers_common.xpath_to_single(articleTree, '/html/body/div[3]/div/div[@class="page-content"]/div[@class="sg-article"]/div[@class="sg-article-text"]', parent=True)
            articleDataDict["descriptions"][i] = curArtDescChilds

    return articleDataDict
