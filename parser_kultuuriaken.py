
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["authors"] = parsers_common.xpath_to("list", pageTree, '//div[@class="list-item"]/div[@class="details"]/div[@class="info"]/p[1]/text()')
    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@class="list-item"]/div[@class="details"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//div[@class="list-item"]/div[@class="image"]/@style')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="list-item"]/div[@class="details"]/h3/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="list-item"]/div[@class="details"]/h3/a/@href')

    # muudame suuna sobivaks
    # articleDataDict = parsers_common.dict_reverse_order(articleDataDict)

    # remove unwanted content: titles
    dictFilters = (
        "ei toimu",
        "jääb ära",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # image
        curArtImage = parsers_common.get(articleDataDict["images"], i, printWarning=0)
        curArtImage = parsers_common.split_failsafe(curArtImage, "url(", 1)
        curArtImage = parsers_common.split_failsafe(curArtImage, "?itok", 0)
        articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImage)

        # url
        curArtUrl = parsers_common.get(articleDataDict["urls"], i)
        curArtUrl = curArtUrl.split("?event")[0]
        articleDataDict["urls"] = parsers_common.list_add_or_assign(articleDataDict["urls"], i, curArtUrl)

        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i):
            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # description
            curArtDesc1 = parsers_common.get(articleDataDict["descriptions"], i)
            curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//article', parent=True)
            curArtDesc2 = curArtDesc2.replace("<h5 class=\"sm-hide\">Galerii</h5>", "")
            curArtDesc2 = curArtDesc2.replace("<h5 class=\"sm-hide\">Tutvustus</h5>", "")
            curArtDesc2 = curArtDesc2.replace("<div class=\"link after-arrow_down sm-show\">Loe lähemalt</div>", "")
            curArtDesc = curArtDesc1 + curArtDesc2
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
