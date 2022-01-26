
import parsers_common
import parsers_datetime
import parsers_html
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 1)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//tbody/tr/th[@class="col-1"]/text()')
    parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//tbody/tr/th[@class="col-7 teemapealkiri"]/a/text()')
    parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//tbody/tr/th[@class="col-4"]/a/@href')

    # remove unwanted content: titles
    dictList = [
        "Lõvide perekonna uus teema",
        "abort",
        "beebi",
        "ivf",
        "lapse",
        "rase ",
        "rased",
        "triibupüüdjad",
    ]
    parentPages = parsers_common.article_data_dict_clean(parentPages, dictList, "in", "titles")

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            curParentUrl = parsers_common.get(parentPages["urls"], i)
            curParentUrl = curParentUrl.split("/#")[0]
            pageTree = parsers_common.get_article_tree(domain, curParentUrl, cache='cacheStamped', pageStamp=parentPages["stamps"][i])

            articlePostsDict = {}
            articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@class="bbp-reply-content entry-content"]', parent=True)
            articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="post_date date updated"]/text()')
            articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="bbp-reply-header entry-title"]/@id')

            # teema postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlePostsDict["urls"], maxArticlePosts):
                # description
                curArtDesc = parsers_common.get(articlePostsDict["descriptions"], j)
                curArtDesc = curArtDesc.split('<div class="gdrts-rating-block ')[0]
                curArtDesc = parsers_html.html_remove_single_parents(curArtDesc)
                articleDataDict["descriptions"] = parsers_common.list_add(articleDataDict["descriptions"], j, curArtDesc)

                # pubDates
                curArtPubDate = parsers_common.get(articlePostsDict["pubDates"], j)
                curArtPubDate = parsers_datetime.guess_datetime(curArtPubDate)
                articleDataDict["pubDates"] = parsers_common.list_add(articleDataDict["pubDates"], j, curArtPubDate)

                # title
                curArtTitle = parsers_common.get(parentPages["titles"], i)
                curArtTitle = parsers_common.str_title_at_domain(curArtTitle, domain)
                articleDataDict["titles"] = parsers_common.list_add(articleDataDict["titles"], j, curArtTitle)

                # url
                curArtUrl = parsers_common.get(parentPages["urls"], i) + "/#" + articlePostsDict["urls"][j]
                articleDataDict["urls"] = parsers_common.list_add(articleDataDict["urls"], j, curArtUrl)

                rss_print.print_debug(__file__, "teema " + str(i + 1) + " postitus nr. " + str(j + 1) + "/(" + str(len(articlePostsDict["urls"])) + ") on " + articlePostsDict["urls"][j], 2)

    # remove unwanted content: descriptions
    dictList = [
        " liba "
        "Kommentaar eemaldatud.",
        "Liba?",
    ]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "descriptions")

    return articleDataDict
