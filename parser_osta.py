
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//article/ul/li/figure/div[@class="offer-thumb__content"]', parent=True)
    articleDataDict["images"] =       parsers_common.xpath_to("list", pageTree, '//article/ul/li/figure/figure/a/@data-original')
    articleDataDict["titles"] =       parsers_common.xpath_to("list", pageTree, '//article/ul/li/figure/div[@class="offer-thumb__content"]/h3/a/text()')
    articleDataDict["urls"] =         parsers_common.xpath_to("list", pageTree, '//article/ul/li/figure/div[@class="offer-thumb__content"]/h3/a/@href')

    # remove unwanted content: titles
    dictList = [
        "az ",
        "jawa",
        "kitarr",
        "poolvääriskivi",
        "tuulesuunaja",
        "viiuli",
        "xtrons",
    ]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "titles")

    return articleDataDict
