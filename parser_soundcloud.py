
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["authors"] =  parsers_common.xpath_to("list", pageTree, '//section/article/h2/a[2]/text()')
    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//section/article/time/text()')
    articleDataDict["titles"] =   parsers_common.xpath_to("list", pageTree, '//section/article/h2/a[@itemprop="url"]/text()')
    articleDataDict["urls"] =     parsers_common.xpath_to("list", pageTree, '//section/article/h2/a[@itemprop="url"]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "2021-01-06T10:11:04Z" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dt%H:%M:%S%z")
        articleDataDict["pubDates"][i] = curArtPubDate

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache="cacheAll")

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//body/div//article', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # image
            curArtImg = parsers_common.xpath_to("single", pageTree, '//body/div//article/p/img/@src')
            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

    return articleDataDict
