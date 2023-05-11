
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//html/body/div/main/div/div/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//html/body/div/main/div/div/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # author
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '//html/body/div/main/article/section/div/p/strong/text()')
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '/html/body/div/main/article/section/div/p', multi=True, parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # pubDate
            curArtPubDate = parsers_common.xpath_to("single", pageTree, '/html/body/div/main/article/header/div[2]/time/@datetime')
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%d")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
