
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//div[@class="col-sm-6"]/div[@class="post-item"]/a/div/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="col-sm-6"]/div[@class="post-item"]/a/h3/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="col-sm-6"]/div[@class="post-item"]/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # images
        curArtImage = parsers_common.get(articleDataDict["images"], i)
        curArtImage = parsers_common.split_failsafe(curArtImage, "?", 0)
        curArtImage = curArtImage.replace("http://", "https://")
        articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImage)

        # titles
        curArtTitle = parsers_common.get(articleDataDict["titles"], i)
        curArtTitle = parsers_common.str_remove_clickbait(curArtTitle)
        articleDataDict["titles"] = parsers_common.list_add_or_assign(articleDataDict["titles"], i, curArtTitle)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # descriptions
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="lead"]', parent=True)
            if not curArtDesc:
                curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="col-sm-9"]/p', multi=True)
            curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@class="text flex-row"]/p', multi=True)
            curArtDesc = curArtDesc + '<br>' + curArtDesc2
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # timeformat magic from "Avaldatud: 14 detsember, 2017" to datetime()
            curArtPubDate = parsers_common.xpath_to("single", pageTree, '//div[@class="col-sm-9"]/div[@class="page-header"]/em/text()')
            curArtPubDate = parsers_datetime.months_to_int(curArtPubDate.split(':')[1])
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d %m, %Y")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
