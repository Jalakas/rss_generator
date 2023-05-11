
import parsers_common
import parsers_datetime
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="history-item"]/p[@class="history-header"]/a[@class="ng-binding"]/text()[1]')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="history-item"]/p[@class="history-header"]/a[@class="ng-binding"]/@href')

    # remove unwanted content: titles
    dictFilters = (
        "Aktuaalne kaamera",
        "ERR-i teleuudised",
        "ETV spordi",
        "Ilm ",
        "Kell ",
        "OTSE ",
        "Päevakaja",
        "Raadiouudised",
        "Viipekeelsed uudised",
        "Ukraina stuudio",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    # muudame artikklite suuna sobivaks
    articleDataDict = parsers_common.dict_reverse_order(articleDataDict)

    iMinus = 0
    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        i = i - iMinus

        # title
        curArtTitle = parsers_common.get(articleDataDict["titles"], i)
        if "|" in curArtTitle:
            curArtTitle = curArtTitle.split("|")[-1]
        articleDataDict["titles"] = parsers_common.list_add_or_assign(articleDataDict["titles"], i, curArtTitle)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # author
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '//article/div[@class="body"]/div/div[@class="meta"]/section/div[@class="byline"]/span', parent=True)
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description
            curArtDesc1 = parsers_common.xpath_to("single", pageTree, '//article/div[@class="body"]/div[@class="lead"]', parent=True)
            curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//article/div[@class="body"]/div[@class="text flex-row"]', parent=True)
            if not curArtDesc2:
                rss_print.print_debug(__file__, "tühja sisuga uudis, eemaldame rea " + str(i), 1)
                articleDataDict = parsers_common.dict_del_article_index(articleDataDict, i)
                iMinus += 1
                continue
            curArtDesc = curArtDesc1 + "<br>" + curArtDesc2
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # image
            curArtImg = parsers_common.xpath_to("single", pageTree, '/html/head/meta[@property="og:image"]/@content')
            if not curArtImg:
                curArtImg = parsers_common.xpath_to("single", pageTree, '/html/head/meta[@property="image"]/@content')
            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

            # pubDates from "2022-02-24T14:20:00+02:00 to datetime()
            curArtPubDate = parsers_common.xpath_to("single", pageTree, '/html/head/meta[@property="article:published_time"]/@content')
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dt%H:%M:%S%z")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
