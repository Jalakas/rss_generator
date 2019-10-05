#!/usr/bin/env python3

import parsers_common
import rss_config


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@id="body1"]/h1/a/@href')

    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@id="body1"]/h1/a', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            pageTree = parsers_common.get_article_tree(session, domain, articleDataDict["urls"][i], noCache=False)

            # description
            curArtDesc = parsers_common.xpath_to_single(pageTree, '//div[@id="body1"]/div[@class="uudis_sisu"]', parent=True)
            articleDataDict["descriptions"].append(curArtDesc)

            # media
            curArtMedia = parsers_common.xpath_to_single(pageTree, '//div[@id="body1"]/div[@class="listeningItem"]/p/audio/source/@src')
            articleDataDict["images"].append(curArtMedia)

    # remove unwanted content
    dictBlacklist = [""]
    dictCond = "=="
    dictField = "images"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    return articleDataDict
