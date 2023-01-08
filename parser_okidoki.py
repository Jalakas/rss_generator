
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//ul/li/div/div/div[@class="horiz-offer-card__content"]/div[@class="horiz-offer-card__desc"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//ul/li/div/div/div[@class="horiz-offer-card__image"]/a/img/@data-src')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//ul/li/div/div/div[@class="horiz-offer-card__image"]/a/@title')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//ul/li/div/div/div[@class="horiz-offer-card__image"]/a/@href')

    # remove unwanted content: titles
    dictFilters = (
        "radiaator",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    articleDataDict = parsers_common.dict_reverse_order(articleDataDict)

    return articleDataDict
