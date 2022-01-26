
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="js-newsline-container"]/span[1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="js-newsline-container"]/div/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="js-newsline-container"]/div/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "14 dets  2017 11:34" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d %m %Y %H:%M")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="news-preview"]/div/text()')
            if not curArtDesc:
                curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="content_item"]', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
