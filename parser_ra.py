#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_config


def fill_article_dict(articleDataDict, pageTree, domain, session):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//li[@class="b-posts__list-item"]/p[@class="b-posts__list-item-summary"]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # timeformat magic from "03.01" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_common.add_to_time_string(curArtPubDate, "%Y.")
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%Y.%d.%m")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            articleTree = parsers_common.get_article_data(session, domain, articleDataDict["urls"][i], mainPage=False)

            # description
            curArtDesc = parsers_common.xpath_to_single(articleTree, '//div[@class="b-article"]', parent=True)
            articleDataDict["descriptions"].append(curArtDesc)

    return articleDataDict
