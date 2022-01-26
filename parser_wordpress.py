
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//body/div[2]/div[1]/main/div/div[3]/div/div/a/h2/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//body/div[2]/div[1]/main/div/div[3]/div/div/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="col-md-12"]', parent=True)
            if not curArtDesc:
                curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="col-md-8"]', parent=True)
            if not curArtDesc:
                curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="img-open-area basic-content pb-4"]', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # image
            curArtImg = parsers_common.xpath_to("single", pageTree, '//a[@data-lightbox="treimages"][1]/@href')
            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

            # pubDates magic from "7. märts 2021" to datetime()
            curArtPubDate = parsers_common.xpath_to("single", pageTree, '//div[@class="col-sm-12 col-md-auto text-sm-center text-md-right"]/div[@class="mt-1 text-uppercase"]/small/text()')
            curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d. %m %Y")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
