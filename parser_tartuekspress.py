#!/usr/bin/env python3

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="forum"][2]/ul/li/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="forum"][2]/ul/li/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            pageTree = parsers_common.get_article_tree(session, domain, articleDataDict["urls"][i], noCache=False)

            # description
            curArtDesc = parsers_common.xpath_to_single(pageTree, '//div[@id="content"]/div[@class="full_width"]', parent=True)
            articleDataDict["descriptions"].append(curArtDesc)

            # author
            try:
                curArtAuthor = curArtDesc
                curArtAuthor = curArtAuthor.split('Autor: <b>')[1]
                curArtAuthor = curArtAuthor.split('</b>')[0]
                articleDataDict["authors"].append(curArtAuthor)
            except Exception as e:
                rss_print.print_debug(__file__, "ei leia autorit, leht on tuksis?", 0)
                rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
                rss_print.print_debug(__file__, "curArtDesc = '" + curArtDesc + "'", 2)

            # it's not possible to make two similar search on same dataset
            pageTree = parsers_common.get_article_tree(session, domain, articleDataDict["urls"][i], noCache=False)

            # image
            curArtMedia = parsers_common.xpath_to_single(pageTree, '//div[@id="content"]/div[@class="full_width"]/a/img[@class="thumb"]/@src')
            articleDataDict["images"].append(curArtMedia)

            # timeformat magic from "13/12/2017 22:24:59" to to datetime()
            curArtPubDate = parsers_common.xpath_to_single(pageTree, '//div[@id="content"]/div[@class="full_width"]/p[*]/i/b[2]/text()')
            curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%d/%m/%Y %H:%M:%S")
            articleDataDict["pubDates"].append(curArtPubDate)

    return articleDataDict
