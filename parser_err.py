#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/p[@class="img"]/a/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/@href')

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]', parent=True)

    # remove unwanted content
    dictBlacklist = ["Aktuaalne kaamera", "Lastetuba", "NOVA", "Ringvaade"]
    dictCond = "in"
    dictField = "titles"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    return articleDataDict
