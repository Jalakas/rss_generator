#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Kuma RSS-voo sisendite parsimine
"""

import hashlib
from lxml import html
import time
import datetime
from time import mktime
import parsers_common

get_article_bodies = False


def extractArticleBody(tree):
    """
    Artikli tervikteksti saamiseks
    """
    body = tree.xpath('//div[@class="news-single-content"]/text()')
    # fulltext = []
    # for elem in body:
        # rawtext = elem.text_content()
        # try:
            # rawtext = rawtext[:rawtext.index('Tweet\n')]
        # except ValueError:
            # None
        # fulltext.append(rawtext)
    # return ''.join(fulltext)
    return body


def getNewsList(newshtml, domain):
    """
    Peameetod kõigi uudiste nimekirja loomiseks
    """
    tree = html.fromstring(newshtml)

    articleIds = []
    articleUrls = tree.xpath('//div[@class="news-list-item-wrapper"]/h3/a/@href')
    articleTitles = tree.xpath('//div[@class="news-list-item-wrapper"]/h3/a/text()')
    articleHeaders = tree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-excerpt"]/p/text()')
    articleImages = tree.xpath('//div[@class="news-list-media"]/img/@src')
    articleBodys = []
    articlePubDate = []

    articlePubDay = tree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/text()[1]')
    articlePubMonth = tree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/span[@class="month"]/text()')
    articlePubYear = tree.xpath('//div[@class="news-list-item-wrapper"]/div[@class="news-list-item-date"]/text()[2]')

    for i in range(0, len(articleUrls) - 1):
        articleUrl = str(domain + articleUrls[i])
        articleUrls[i] = articleUrl

        # generate unical id from link
        articleIds.append(hashlib.md5(articleUrl.encode('utf-8')).hexdigest())

        articleImage = str(domain + articleImages[i])
        articleImages[i] = articleImage

        if (get_article_bodies is True):
            articleTree = parsers_common.getArticleData(articleUrl)

            # todo(BROKEN)
            buf = extractArticleBody(articleTree)
            print(buf)
            articleBodys.append(buf)

            articlePubDateRaw = parsers_common.treeExtract(articleTree, '//div[@class="news-single-timedata"]/text()')

            # timeformat magic from "13 dets  17" to datetime()
            articlePubDateRaw = articlePubDateRaw.strip().replace('  ', ' ')
            articlePubDateRaw = articlePubDateRaw.replace('jaan', '01').replace('veeb', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
            articlePubDateRaw = articlePubDateRaw.replace('juuli', '07').replace('aug', '08').replace('sept', '09').replace('okt', '10').replace('nov', '11').replace('dets', '12')
            articlePubDate.append(datetime.datetime.fromtimestamp(mktime(time.strptime(articlePubDateRaw, "%d %m %y"))), )  # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        else:
            if i < len(articlePubYear) and (int(articlePubYear[i].strip()) > 2016):
                curYear = articlePubYear[i].strip()
            articlePubDateRaw = articlePubDay[i].strip() + " " + articlePubMonth[i].strip() + " " + curYear
            articlePubDateRaw = datetime.datetime.fromtimestamp(mktime(time.strptime(articlePubDateRaw, "%d %m %Y")))
            articlePubDate.append(articlePubDateRaw)

    return {"articleIds": articleIds,
            "articleUrls": articleUrls,
            "articleTitles": articleTitles,
            "articleHeaders": articleHeaders,
            "articleImages": articleImages,
            "articleBodys": articleBodys,
            "articlePubDate": articlePubDate,
            }
