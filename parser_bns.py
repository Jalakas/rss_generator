#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_config


def fill_article_dict(articleDataDict, pageTree, domain, session):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/span[1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/div/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/div/a/@href')

    articleDescriptionsTag = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/div/span[1]/text()')
    articleDescriptionsRaw = parsers_common.xpath_to_list(pageTree, '//div[@class="js-newsline-container"]/div/a/text()')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # timeformat magic from "14 dets  2017 11:34" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_common.months_to_int(curArtPubDate)
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d %m %Y %H:%M")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            articleTree = parsers_common.get_article_data(session, domain, articleDataDict["urls"][i], mainPage=False)

            # description
            curArtDesc = parsers_common.xpath_to_single(articleTree, '//div[@class="news-preview"]/div/text()')
            articleDataDict["descriptions"].append(curArtDesc)
        else:
            # description
            articleDataDict["descriptions"].append(articleDescriptionsTag[i] + "<br>" + articleDescriptionsRaw[i])

    return articleDataDict
