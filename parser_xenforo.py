
import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 4)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//div[@class="reply-count"]/span[@data-xf-init="tooltip"]/@title')
    parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@qid="thread-item-parent"]/div[@qid="thread-item"]/div/h3[@class="structItem-title"]/a[@qid="thread-item-title"]/text()')
    parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@qid="thread-item-parent"]/div[@qid="thread-item"]/div/h3[@class="structItem-title"]/a[@qid="thread-item-title"]/@href')

    # remove unwanted content: titles
    dictFilters = (
        "$",
        "*:::::::the official what did you do to you mkiv today thread::::::::*",
        "??",
        "Ask a Simple Question",
    )
    parentPages = parsers_common.article_data_dict_clean(__file__, parentPages, dictFilters, "in", "titles")

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            curParentUrl = parsers_common.get(parentPages["urls"], i)
            curParentUrl = curParentUrl + "page-1000"
            parentPagesStamp = parsers_common.get(parentPages["stamps"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curParentUrl, cache='cacheStamped', pageStamp=parentPagesStamp)

            articlePostsDict = {}
            articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//h4[@qid="message-username"]//text()')
            articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//article/div[@class="bbWrapper"]', parent=True)
            articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="message-attribution-main"]/a[@class="u-concealed"][2]/time/@datetime')
            articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="message-attribution-main"]/a[@class="u-concealed"][2]/@href')

            # teema postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlePostsDict["urls"], maxArticlePosts):
                # author
                curArtAuthor = parsers_common.get(articlePostsDict["authors"], j)
                articleDataDict["authors"] = parsers_common.list_add(articleDataDict["authors"], j, curArtAuthor)

                # description
                curArtDesc = parsers_common.get(articlePostsDict["descriptions"], j)
                articleDataDict["descriptions"] = parsers_common.list_add(articleDataDict["descriptions"], j, curArtDesc)

                # pubDates
                curArtPubDate = parsers_common.get(articlePostsDict["pubDates"], j)
                curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dT%H:%M:%S%z")  # 2021-01-28T16:15:42-0500
                articleDataDict["pubDates"] = parsers_common.list_add(articleDataDict["pubDates"], j, curArtPubDate)

                # title
                curArtTitle = parsers_common.get(parentPages["titles"], i)
                curArtTitle = parsers_common.str_title_at_domain(curArtTitle, domain)
                articleDataDict["titles"] = parsers_common.list_add(articleDataDict["titles"], j, curArtTitle)

                # url
                curArtUrl = parsers_common.get(articlePostsDict["urls"], j)
                articleDataDict["urls"] = parsers_common.list_add(articleDataDict["urls"], j, curArtUrl)

                rss_print.print_debug(__file__, "teema " + str(i + 1) + " postitus nr. " + str(j + 1) + "/(" + str(len(articlePostsDict["urls"])) + ") on " + articlePostsDict["urls"][j], 2)

    return articleDataDict
