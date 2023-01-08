
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//div[@class="image session__image"]/img/@data-srcset')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//h2[@class="session__title"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//a[@class="session__link"]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):

        curArtPubImage = parsers_common.get(articleDataDict["images"], i)
        if " " in curArtPubImage:
            curArtPubImages = curArtPubImage.split(" ")
            curArtPubImage = curArtPubImages[-2]
            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtPubImage)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="film-detail__main"]', parent=True)
            if not curArtDesc:
                curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="text editor"]', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
