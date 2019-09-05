#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import parsers_common
import rss_print


def article_dict(articleDataDict, pageTree, domain, maxArticleBodies, getArticleBodies):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//main/div[1]/div/div/section[@class="card cf"]/hgroup[@class="card-title"]/h1/a/span/@title')
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//main/div[1]/div/div/section[@class="card cf"]//a/div/img/@scr')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//main/div[1]/div/div/section[@class="card cf"]/hgroup[@class="card-title"]/h1/a/span/@title')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//main/div[1]/div/div/section[@class="card cf"]/hgroup[@class="card-title"]/h1/a/@href')

    # remove unwanted content
    k = 0
    while (k < len(articleDataDict["urls"])):
        rss_print.print_debug(__file__, "kontrollime kannet" + str(k + 1) + "/" + str(len(articleDataDict["urls"])) + ": " + articleDataDict["titles"][k], 3)
        if (
                articleDataDict["titles"][k].find("(uus) raamat") >= 0 or
                articleDataDict["titles"][k].find("Abramova") >= 0 or
                articleDataDict["titles"][k].find("Based Broccoli") >= 0 or
                articleDataDict["titles"][k].find("Bisweed") >= 0 or
                articleDataDict["titles"][k].find("EKKM") >= 0 or
                articleDataDict["titles"][k].find("ERROR!") >= 0 or
                articleDataDict["titles"][k].find("Floorshow") >= 0 or
                articleDataDict["titles"][k].find("Gnoom") >= 0 or
                articleDataDict["titles"][k].find("Hillbilly Picnic") >= 0 or
                articleDataDict["titles"][k].find("IDA Jutud") >= 0 or
                articleDataDict["titles"][k].find("IDA Räpp") >= 0 or
                articleDataDict["titles"][k].find("Keskkonnatund") >= 0 or
                articleDataDict["titles"][k].find("Kink Konk") >= 0 or
                articleDataDict["titles"][k].find("Korrosioon") >= 0 or
                articleDataDict["titles"][k].find("Kräpp") >= 0 or
                articleDataDict["titles"][k].find("Let Me Juke") >= 0 or
                articleDataDict["titles"][k].find("Lunchbreak Lunchdate") >= 0 or
                articleDataDict["titles"][k].find("Meie igapäevane avalik ruum") >= 0 or
                articleDataDict["titles"][k].find("Muster") >= 0 or
                articleDataDict["titles"][k].find("Müürilehe Hommik") >= 0 or
                articleDataDict["titles"][k].find("Paneel") >= 0 or
                articleDataDict["titles"][k].find("Playa Music") >= 0 or
                articleDataDict["titles"][k].find("Propel") >= 0 or
                articleDataDict["titles"][k].find("Puhkus") >= 0 or
                articleDataDict["titles"][k].find("Room_202") >= 0 or
                articleDataDict["titles"][k].find("Rõhk") >= 0 or
                articleDataDict["titles"][k].find("SAAL RAADIO") >= 0 or
                articleDataDict["titles"][k].find("Soojad Suhted") >= 0 or
                articleDataDict["titles"][k].find("Soojad suhted") >= 0 or
                articleDataDict["titles"][k].find("Triinemets & Co.") >= 0 or
                articleDataDict["titles"][k].find("Vitamiin K") >= 0 or
                articleDataDict["titles"][k].find("Zubrovka AM") >= 0 or
                articleDataDict["titles"][k].find("Ära Kaaguta!") >= 0 or
                articleDataDict["titles"][k].find("Ära kaaguta!") >= 0
        ):
            articleDataDict = parsers_common.del_article_dict_index(articleDataDict, k)
        else:
            k += 1

    return articleDataDict
