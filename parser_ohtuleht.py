
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//a[@class="styled-link__type-1"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//a[@class="styled-link__type-1"]/@href')

    # remove unwanted content: titles
    dictFilters = (
        "Ristiku Ristsõnad:",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # titles
        curArtTitle = parsers_common.get(articleDataDict["titles"], i)
        curArtTitle = parsers_common.str_remove_clickbait(curArtTitle)
        articleDataDict["titles"] = parsers_common.list_add_or_assign(articleDataDict["titles"], i, curArtTitle)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # author
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '//span[@class="author"]/text()')
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description
            curArtDesc1 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-main--content article-main--excerpt formatted--content"]', parent=True)
            curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-main--content formatted--content"]', parent=True, multi=True)

            curArtDesc = curArtDesc1 + '<br>' + curArtDesc2
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # image
            curArtImg = parsers_common.xpath_to("single", pageTree, '//meta[@property="og:image"]/@content')
            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

            # pubDates from "29. juuni 2022 18:36" to datetime()
            curArtPubDate = parsers_common.xpath_to("single", pageTree, '//div[@class="article-main--details--inner flex align-items-center"]/@data-date')
            curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d. %m %Y %H:%M")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
