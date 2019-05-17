#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod kõigi objektide nimekirja loomiseks
    """

    articleDescriptions = parsers_common.xpath(pageTree, '//main/div[1]/div/div/section[@class="card cf"]//h1/a/span/@title')
    articleImages = parsers_common.xpath(pageTree, '//main/div[1]/div/div/section[@class="card cf"]//a/div/img/@scr')
    articlePubDates = []
    articleTitles = parsers_common.xpath(pageTree, '//main/div[1]/div/div/section[@class="card cf"]//h1/a/span/@title')
    articleUrls = parsers_common.xpath(pageTree, '//main/div[1]/div/div/section[@class="card cf"]//h1/a/@href')

    # remove unwanted content
    j = 0
    while (j < min(len(articleUrls), maxArticleCount)):
        rss_print.print_debug(__file__, "kontrollime kannet: " + str(j + 1) + ", kokku: " + str(len(articleUrls)), 3)
        if (
            articleTitles[j].find("(uus) raamat") >= 0 or
            articleTitles[j].find("Abramova") >= 0 or
            articleTitles[j].find("Bisweed") >= 0 or
            articleTitles[j].find("ERROR!") >= 0 or
            articleTitles[j].find("Floorshow") >= 0 or
            articleTitles[j].find("Gnoom") >= 0 or
            articleTitles[j].find("IDA Jutud") >= 0 or
            articleTitles[j].find("Keskkonnatund") >= 0 or
            articleTitles[j].find("Lunchbreak Lunchdate") >= 0 or
            articleTitles[j].find("Muster") >= 0 or
            articleTitles[j].find("Paneel") >= 0 or
            articleTitles[j].find("Room_202") >= 0 or
            articleTitles[j].find("Rõhk") >= 0 or
            articleTitles[j].find("SAAL RAADIO") >= 0 or
            articleTitles[j].find("Soojad suhted") >= 0 or
            articleTitles[j].find("Vitamiin K") >= 0 or
            articleTitles[j].find("Ära kaaguta!") >= 0
        ):
            rss_print.print_debug(__file__, "eemaldame halva sisu kande: " + articleTitles[j], 0)

            articleDescriptions = parsers_common.del_if_set(articleDescriptions, j)
            articleImages = parsers_common.del_if_set(articleImages, j)
            articlePubDates = parsers_common.del_if_set(articlePubDates, j)
            articleTitles = parsers_common.del_if_set(articleTitles, j)
            articleUrls = parsers_common.del_if_set(articleUrls, j)
        else:
            j += 1

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
