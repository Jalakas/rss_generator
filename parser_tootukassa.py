#!/usr/bin/env python3

import parsers_datetime
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/p', parent=True)
    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="right-content"]/div[@class="application-date"][1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # url
        curArtUrl = articleDataDict["urls"][i]
        curArtUrl = curArtUrl.split('?ref=')[0]
        articleDataDict["urls"][i] = curArtUrl

        # timeformat magic from "Avaldatud: 12.12.2017" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = curArtPubDate.split(': ')[1]
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d.%m.%Y")
        articleDataDict["pubDates"][i] = curArtPubDate

    return articleDataDict
