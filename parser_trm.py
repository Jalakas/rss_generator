
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//div[@class="product"]/div[@class="image-cell"]/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="product"]/div[@class="description-cell"]/h2/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="product"]/div[@class="description-cell"]/a/@href')

    articlePrices = parsers_common.xpath_to("list", pageTree, '//div[@class="product"]/div[@class="price-cell"]', parent=True)
    articleDescriptions = parsers_common.xpath_to("list", pageTree, '//div[@class="product"]/div[@class="description-cell"]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtDesc = parsers_common.get(articlePrices, i) + parsers_common.get(articleDescriptions, i)
        articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
