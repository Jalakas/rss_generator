#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="right-content"]/div[@class="application-date"][1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/p', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # clean up url
        articleDataDict["urls"][i] = articleDataDict["urls"][i].split('?ref=')[0]

        # timeformat magic from "Avaldatud: 12.12.2017" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i].split(': ')[1]
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d.%m.%Y")
        articleDataDict["pubDates"][i] = curArtPubDate

        # description
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

    return articleDataDict
