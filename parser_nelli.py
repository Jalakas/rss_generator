#!/usr/bin/env python3

import parsers_datetime
import parsers_common
import rss_config


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-cnt"]/div[@class="sb-article-prolog"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-image"]/@style')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-cnt"]/div[@class="sb-article-title"]/h3/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            pageTree = parsers_common.get_article_tree(session, domain, articleDataDict["urls"][i], noCache=False)

            # author
            curArtAuthor = parsers_common.xpath_to_single(pageTree, '//div[@class="sg-article-details"]/div[@class="author"]/text()')
            articleDataDict["authors"].append(curArtAuthor)

            # description
            curArtDesc = parsers_common.xpath_to_single(pageTree, '/html/body/div[3]/div/div[@class="page-content"]/div[@class="sg-article"]/div[@class="sg-article-text"]', parent=True)
            articleDataDict["descriptions"][i] = curArtDesc

            # timeformat magic from "18.08.2019 21:35" to datetime()
            curArtPubDate = parsers_common.xpath_to_single(pageTree, '//div[@class="sg-article-details"]/div[@class="date"]/text()')
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")
            articleDataDict["pubDates"].append(curArtPubDate)

    return articleDataDict
