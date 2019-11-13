#!/usr/bin/env python3

import parsers_datetime
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["authors"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div[@class="section messages"]/div[@class="message"]/div[@class="name"]', parent=True)
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
        curArtTitle = parsers_common.lchop(articleDataDict["titles"][i], "Re: ")
        curArtTitle = parsers_common.title_at_domain(curArtTitle, domain)
        articleDataDict["titles"][i] = curArtTitle

        # timeformat magic from "20:22 01.09.2019" to Datetime()
        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "eile", "%d.%m.%Y", offSetDays=-1)
        curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "täna", "%d.%m.%Y", offSetDays=0)
        curArtPubDate = parsers_datetime.add_missing_date_to_string(curArtPubDate, "%H:%M %d.%m.%Y", " %d.%m.%Y")
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%H:%M %d.%m.%Y")
        articleDataDict["pubDates"][i] = curArtPubDate

    return articleDataDict
