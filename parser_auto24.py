#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, session):

    articleDataDict["authors"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div[@class="section messages"]/div[@class="message"]/div[@class="name"]//text()[1]')
    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div[@class="section messages"]/div[@class="message"]/div[@class="content"]', parent=True)
    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div[@class="section messages"]/div[@class="message"]/div[@class="posttime"]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div[@class="section messages"]/div[@class="message"]/div[@class="title"]/a[3]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div[@class="section messages"]/div[@class="message"]/div[@class="title"]/a[3]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtDesc = articleDataDict["descriptions"][i]
        curArtDesc = curArtDesc.split('<div class="userControls')[0]
        curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
        articleDataDict["descriptions"][i] = curArtDesc

        # title
        articleDataDict["titles"][i] = articleDataDict["titles"][i] + " @auto24.ee"

        # timeformat magic from "20:22 01.09.2019" to datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_common.replace_string_with_timeformat(curArtPubDate, "eile", "%d.%m.%Y", offSetDays=-1)
        curArtPubDate = parsers_common.replace_string_with_timeformat(curArtPubDate, "täna", "%d.%m.%Y", offSetDays=0)
        if len(curArtPubDate) < len("%H:%M %d.%m.%Y"):
            curArtPubDate = parsers_common.add_to_time_string(curArtPubDate, "%d.%m.%Y ")
            rss_print.print_debug(__file__, "lisasime kuupäevale 'kuupäeva' osa: " + curArtPubDate, 3)
        curArtPubDate = parsers_common.raw_to_datetime(curArtPubDate, "%H:%M %d.%m.%Y")
        articleDataDict["pubDates"][i] = curArtPubDate

    return articleDataDict
