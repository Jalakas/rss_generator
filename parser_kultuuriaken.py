#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/a[@class="image"]/@style')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]/a[1]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]/a[1]/@href')
    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # image
        curArtImage = articleDataDict["images"][i]
        curArtImage = curArtImage.split("'")[1]
        articleDataDict["images"][i] = curArtImage

        # url
        curArtUrl = articleDataDict["urls"][i]
        curArtUrl = curArtUrl.split("?event=")[0]
        articleDataDict["urls"][i] = curArtUrl

    # remove unwanted content
    dictBlacklist = [
        "Jääb ära"
    ]
    dictCond = "in"
    dictField = "titles"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    # newest events last for feedly ordering
    articleDataDict["images"].reverse()
    articleDataDict["titles"].reverse()
    articleDataDict["urls"].reverse()
    articleDataDict["descriptions"].reverse()

    return articleDataDict
