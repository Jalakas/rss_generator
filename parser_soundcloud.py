#!/usr/bin/env python3

import parsers_datetime
import parsers_common
import rss_config


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["authors"] = parsers_common.xpath_to_list(pageTree,   '//section/article/h2/a[2]/text()')
    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree,  '//section/article/time/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree,    '//section/article/h2/a[@itemprop="url"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree,      '//section/article/h2/a[@itemprop="url"]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # timeformat magic from "2021-01-06T10:11:04Z" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dT%H:%M:%SZ")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            pageTree = parsers_common.get_article_tree(session, domain, articleDataDict["urls"][i], noCache=False)

            # description
            curArtDesc = parsers_common.xpath_to_single(pageTree, '//article/header', parent=True)
            articleDataDict["descriptions"].append(curArtDesc)

            # image
            curArtImg = parsers_common.xpath_to_single(pageTree, '//article/p/img/@src')
            articleDataDict["images"].append(curArtImg)

    return articleDataDict
