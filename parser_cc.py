
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//article/a/div/div/img/@src')
    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//article/a/div[@class="node__body"]/p[@class="node__date"]/span/@content')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//article/a/div[@class="node__body"]/h3/span/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//article/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "2021-03-23T12:35:36+00:00" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dt%H:%M:%S%z")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="node__content"]/div/div[@class="field__item"]', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
