
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//table[@class="views-table cols-5"]/tbody/tr', parent=True)
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[1]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//table[@class="views-table cols-5"]/tbody/tr/td[5]/div[1]/a/@href')

    # remove unwanted content: descriptions
    dictList = [
        "ametnik",
        "hooldaja",
        "jurist",
        "koristaja",
        "logopeed",
        "pedagoog",
        "psühholoog",
        "raamatupidaja",
        "sanitar",
        "teenindaja",
        "uurija",
        "õpetaja",
    ]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "titles")

    return articleDataDict
