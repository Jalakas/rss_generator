
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    author =                    parsers_common.xpath_to("single", pageTree, '//p[@id="band-name-location"]/span[@class="title"]/text()')
    description =               parsers_common.xpath_to("single", pageTree, '//meta[@name="description"]/@content')
    domain =                    parsers_common.xpath_to("single", pageTree, '//meta[@property="og:url"]/@content')

    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//div[@class="leftMiddleColumns"]/ol/li/a/div/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="leftMiddleColumns"]/ol/li/a/p/text()')
    articleDataDict["urls"] =   parsers_common.xpath_to("list", pageTree, '//div[@class="leftMiddleColumns"]/ol/li/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # author
        articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, author)

        # description
        articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, description)

        # title
        curArtTitle = parsers_common.get(articleDataDict["titles"], i)
        curArtTitle = parsers_common.str_title_at_domain(curArtTitle, domain)
        articleDataDict["titles"] = parsers_common.list_add_or_assign(articleDataDict["titles"], i, curArtTitle)

        # url
        curArtUrl = parsers_common.get(articleDataDict["urls"], i)
        articleDataDict["urls"] = parsers_common.list_add_or_assign(articleDataDict["urls"], i, curArtUrl)

    return articleDataDict
