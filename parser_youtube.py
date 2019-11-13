#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//div[@class="text-wrapper style-scope ytd-video-renderer"]/yt-formatted-string[@id="description-text"]/text()')
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//a[@id="thumbnail"]/yt-img-shadow/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="text-wrapper style-scope ytd-video-renderer"]/div[@id="meta"]/div[@id="title-wrapper"]/h3/a[@id="video-title"]/@title')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="text-wrapper style-scope ytd-video-renderer"]/div[@id="meta"]/div[@id="title-wrapper"]/h3/a[@id="video-title"]/@href')

    return articleDataDict
