#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//main/div[1]/div/div/section[@class="card cf"]/hgroup[@class="card-title"]/h1/a/span/@title')
#   articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//main/div[1]/div/div/section[@class="card cf"]/hgroup[@class="card-title"]/a[@class="album-art"]/div[@class="album-artwork"]/img/@scr')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//main/div[1]/div/div/section[@class="card cf"]/hgroup[@class="card-title"]/h1/a/span/@title')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//main/div[1]/div/div/section[@class="card cf"]/hgroup[@class="card-title"]/h1/a/@href')

    # remove unwanted content
    dictBlacklist = [
        "(uus) raamat", "Abramova", "Based Broccoli", "Beats of No Nation", "Bisweed", "EKKM", "ERROR!", "Floorshow", "Gnoom", "Hard Feeler", "Hillbilly Picnic", "IDA Jutud", "IDA Räpp", "Intro",
        "Katus", "Keskkonnatund", "Kink Konk", "Korrosioon", "Kräpp", "Let Me Juke", "Liin ", "LIIN", "Lunchbreak Lunchdate", "Meie igapäevane avalik ruum", "Muster", "Müürilehe Hommik", "N-LIB"
        "Paneel", "Playa Music", "Propel", "Puhkus", "Oleneb päevast!", "Rets Records", "Room_202", "Rõhk", "SAAL Raadio", "SAAL RAADIO", "Soojad Suhted", "Soojad suhted", "Svet Nureka", "Söökladisko",
        "Triinemets.", "Vitamiin K", "Zubrovka AM", "Ära Kaaguta!", "Ära kaaguta!"
        ]
    dictCond = "in"
    dictField = "titles"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    return articleDataDict
