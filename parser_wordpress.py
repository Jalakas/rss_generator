
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//a[@class="uu-list-title"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//a[@class="uu-list-title"]/@href')

    # remove unwanted content: titles
    dictFilters = (
        "Päeva sõel (med.):",
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
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '/html/head/meta[@name="twitter:data1"]/@content')
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="col-12 col-lg-8 mx-lg-auto uu-content-text"]', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # image
            curArtImg = parsers_common.xpath_to("single", pageTree, '/html/head/meta[@property="og:image"]/@content')
            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

            # pubDates magic from "2022-10-23T10:11:18+00:00" to datetime()
            curArtPubDate = parsers_common.xpath_to("single", pageTree, '/html/head/meta[@property="article:published_time"]/@content')
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dt%H:%M:%S%z")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
