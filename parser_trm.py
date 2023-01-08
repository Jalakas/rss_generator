
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@class="product details product-item-details"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//img[@class="image_hover"]/@data-src')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//a[@class="product-item-link"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//a[@class="product-item-link"]/@href')

    return articleDataDict
