#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Lõunaeestlane RSS-voo sisendite parsimine
"""

from lxml import html
import parsers_common

get_article_bodies = False


def getNewsList(newshtml, domain):
    """
    Peameetod kõigi uudiste nimekirja loomiseks
    """
    tree = html.fromstring(newshtml)

    articleDescriptions = tree.xpath('//div[@class="midColPost"]/p/text()')
    articleIds = []
    articleImages = tree.xpath('//div[@class="midColPost"]/a/img/@src')
    articlePubDates = []
    articleTitles = tree.xpath('//div[@class="midColPost"]/h2/a/@title')
    articleUrls = tree.xpath('//div[@class="midColPost"]/h2/a/@href')

    articlePubDatesRaw = tree.xpath('//div[@class="midColPost"]/span/text()[1]')

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unical id from link
        articleIds.append(articleUrl.split("?p=")[1])

        # timeformat magic from "15. detsember 2017 / " to datetime()
        curArtPubDate = articlePubDatesRaw[i]
        curArtPubDate = curArtPubDate.replace('jaanuar', '01').replace('veebruar', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
        curArtPubDate = curArtPubDate.replace('juuli', '07').replace('august', '08').replace('september', '09').replace('oktoober', '10').replace('november', '11').replace('detsember', '12').replace('  ', ' ')
        curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d. %m %Y / ")
        articlePubDates.append(curArtPubDate)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
