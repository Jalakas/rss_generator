
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//li[@class="b-posts__list-item"]/p[@class="b-posts__list-item-summary"]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//li[@class="b-posts__list-item"]/h2[@class="b-posts__list-item-title"]/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "30.01.2021" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d.%m.%Y")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="b-article"]', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
