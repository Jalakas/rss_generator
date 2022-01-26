
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//div[@class="product_camp_box w"]/a/div[@class="product_camp"]/div[@class="leftC"]/div/img/@data-src')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="product_camp_box w"]/a/div[@class="product_camp"]/div[@class="leftC"]/h3/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="product_camp_box w"]/a/@href')

    articlePrices = parsers_common.xpath_to("list", pageTree, '//div[@class="product_camp_box w"]/div[@class="priceCont"]', parent=True)
    articleDescriptions = parsers_common.xpath_to("list", pageTree, '//div[@class="product_camp_box w"]/a/div[@class="product_camp"]/div[@class="leftC"]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtDesc = articlePrices[i] + articleDescriptions[i]
        curArtDesc = curArtDesc.replace('<img src="https://www.stokker.ee/gfx/blank.gif">', "")
        articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

        # image
        curArtImg = parsers_common.get(articleDataDict["images"], i)
        curArtImg = curArtImg.split("?")[0]
        curArtImg = curArtImg.replace("%26", "&")
        articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

    return articleDataDict
