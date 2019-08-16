#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    articleDataDict["descriptions"] = []
    articleDataDict["images"] = []
    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/span[1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/div/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/div/a/@href')

    articleDescriptionsTag = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/div/span[1]/text()')
    articleDescriptionsRaw = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/div/a/text()')

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        # timeformat magic from "14 dets  2017 11:34" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_common.monthsToNumber(curArtPubDate)
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d %m %Y %H:%M")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (getArticleBodies is True):
            # load article into tree
            articleTree = parsers_common.getArticleData(domain, articleDataDict["urls"][i], False)

            # description
            curArtDescChilds = parsers_common.xpath_parent_to_single(articleTree, '//div[@class="news-preview"]/div')
            articleDataDict["descriptions"].append(curArtDescChilds)
        else:
            # description
            articleDataDict["descriptions"].append(articleDescriptionsTag[i] + "<br>" + articleDescriptionsRaw[i])

    return articleDataDict
