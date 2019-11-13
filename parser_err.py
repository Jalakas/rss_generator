#!/usr/bin/env python3

import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/p[@class="img"]/a/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/@href')

    # remove unwanted content
    dictBlacklist = ["Aktuaalne kaamera", "Insight", "Johannese lähetamine", "Kes keda?", "Lasteekraan", "Lastetuba", "NOVA", "Ongi Koik", "OP:", "Plekktrumm", "Ringvaade", "Taevavalvurid", "Tähendamisi"]
    dictCond = "in"
    dictField = "titles"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    return articleDataDict
