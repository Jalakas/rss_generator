
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["authors"] =          parsers_common.xpath_to("list", pageTree, '//ul[@class="results search-row list-unstyled"]/li/div[2]/div[@class="inner"]/div/@title')
    articleDataDict["descriptions"] =     parsers_common.xpath_to("list", pageTree, '//ul[@class="results search-row list-unstyled"]/li/div[3]/div/div/div', parent=True)
    articleDataDict["images"] =           parsers_common.xpath_to("list", pageTree, '//ul[@class="results search-row list-unstyled"]/li/div[2]/div[@class="inner"]/a/img/@src')
    articleDataDict["titles"] =           parsers_common.xpath_to("list", pageTree, '//ul[@class="results search-row list-unstyled"]/li/div[3]/div/h2/a/text()')
    articleDataDict["urls"] =             parsers_common.xpath_to("list", pageTree, '//ul[@class="results search-row list-unstyled"]/li/div[3]/div/h2/a/@href')

    return articleDataDict
