
import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 5)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="meta"][4]/span/text()')
    parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="title"]/a/@title')
    parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//table[@class="grid zebra forum"]/tr/td[@class="title"]/a/@href')

    # remove unwanted content: titles
    dictFilters = (
        "Börsihai",
        "Cleveroni aktsiate ost/müük/oksjon",
        "Head uut aastat – prognoosid",
        "Keegi malet soovib mängida",
        "LHV Pank paremaks",
        "Muudatused analüütikute hinnangutes",
        "Sport!",
        "Uurimis- ja lõputööde küsimustikud",
    )
    parentPages = parsers_common.article_data_dict_clean(__file__, parentPages, dictFilters, "in", "titles")

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            curParentUrl = parsers_common.get(parentPages["urls"], i) + '?listEventId=jumpToPage&listEventParam=100&pagesOfMaxSize=true'
            parentPagesStamp = parsers_common.get(parentPages["stamps"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curParentUrl, cache='cacheStamped', pageStamp=parentPagesStamp)

            articlePostsDict = {}
            articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/p[@class="author"]/strong/a/text()')
            articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-content temporary-class"]', parent=True)
            articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/node()')
            articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/@href')

            # teema postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlePostsDict["urls"], maxArticlePosts):
                # author
                curArtAuthor = parsers_common.get(articlePostsDict["authors"], j)
                articleDataDict["authors"] = parsers_common.list_add(articleDataDict["authors"], j, curArtAuthor)

                # description
                articleDataDict["descriptions"] = parsers_common.list_add(articleDataDict["descriptions"], j, parsers_common.get(articlePostsDict["descriptions"], j))

                # pubDates magic from "15.01.2012 23:49" to datetime()
                curArtPubDate = parsers_common.get(articlePostsDict["pubDates"], j)
                curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "Eile", "%d.%m.%Y", offsetDays=-1)
                curArtPubDate = parsers_datetime.add_missing_date_to_string(curArtPubDate, "%d.%m.%Y %H:%M", "%d.%m.%Y ")
                curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")
                articleDataDict["pubDates"] = parsers_common.list_add(articleDataDict["pubDates"], j, curArtPubDate)

                # title
                curArtTitle = parsers_common.get(parentPages["titles"], i)
                curArtTitle = parsers_common.str_title_at_domain(curArtTitle, domain)
                articleDataDict["titles"] = parsers_common.list_add(articleDataDict["titles"], j, curArtTitle)

                # url
                curArtUrl = parentPages["urls"][i] + articlePostsDict["urls"][j]
                articleDataDict["urls"] = parsers_common.list_add(articleDataDict["urls"], j, curArtUrl)

                rss_print.print_debug(__file__, "teema postitus nr. " + str(j + 1) + "/(" + str(len(articlePostsDict["urls"])) + ") on " + articlePostsDict["urls"][j], 2)

    return articleDataDict
