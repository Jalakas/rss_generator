
import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 8)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    version = 0
    if "kipper.ee" in domain or "militaar.net" in domain:
        version = 1
        parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//table[@class="tablebg"]//tr/td/p[@class="topicdetails"]/text()')
        parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//table[@class="tablebg"]//tr/td/a[@class="topictitle"]/text()')
        parentPages["urls"] =   parsers_common.xpath_to("list", pageTree, '//table[@class="tablebg"]//tr/td/a[@class="topictitle"]/@href')
    else:
        parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl/dd[@class="posts"]/text()')
        parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl/*/div/a[@class="topictitle"]/text()')
        parentPages["urls"] =   parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl/*/div/a[@class="topictitle"]/@href')

    if not parentPages["urls"] and "arutelud.com" in domain:
        rss_print.print_debug(__file__, "aktiivseid teemasid ei leitud, arutelude foorumis külastame mammutteemat", 1)
        parentPages["stamps"] = parsers_common.list_add_or_assign(parentPages["stamps"], 0, "")
        parentPages["titles"] = parsers_common.list_add_or_assign(parentPages["titles"], 0, "Arutelud")
        parentPages["urls"] =   parsers_common.list_add_or_assign(parentPages["urls"], 0, "https://arutelud.com/viewtopic.php?f=3&t=4&sd=d&sk=t&st=7")

    # remove unwanted content: titles
    dictList = [
        "Race.Fi:",
        "Write my",
        "PÕLVAMAA, VÕRUMAA JA VALGAMAA CB JA HAM SIDE",
    ]
    parentPages = parsers_common.article_data_dict_clean(parentPages, dictList, "in", "titles")

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            curParentUrl = parsers_common.get(parentPages["urls"], i)
            curParentUrl = curParentUrl.split("&sid=")[0]
            curParentUrl = curParentUrl + "&start=100000"
            parentPagesStamp = parsers_common.get(parentPages["stamps"], i)
            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curParentUrl, cache='cacheStamped', pageStamp=parentPagesStamp)

            articlePostsDict = {}
            if version in (1, 2):
                rss_print.print_debug(__file__, "kasutame spetsiifilist hankimist, domain = " + domain, 2)
                articlePostsDict["authors"] =       parsers_common.xpath_to("list", pageTree, '//tr/td/b[@class="postauthor"]/text()')
                articlePostsDict["descriptions"] =  parsers_common.xpath_to("list", pageTree, '//tr/td/div[@class="postbody"][1]', parent=True)
                articlePostsDict["pubDates"] =      parsers_common.xpath_to("list", pageTree, '//tr/td[@class="gensmall"]/div[@style="float: right;"]/text()')
                articlePostsDict["urls"] =          parsers_common.xpath_to("list", pageTree, '//tr/td[@class="gensmall"]/div[@style="float: right;"]/a/@href')
            else:
                rss_print.print_debug(__file__, "kasutame üldist hankimist, domain = " + domain, 3)
                articlePostsDict["authors"] =       parsers_common.xpath_to("list", pageTree, '//p[@class="author"]//strong//text()')
                articlePostsDict["descriptions"] =  parsers_common.xpath_to("list", pageTree, '//div[@class="content"]', parent=True)
                articlePostsDict["pubDates"] =      parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/time/@datetime')
                articlePostsDict["urls"] =          parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/a/@href')

                if not articlePostsDict["pubDates"]:
                    articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/time/text()')
                if not articlePostsDict["pubDates"]:
                    articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/text()[1]')
                if len(articlePostsDict["pubDates"][0]) < 5:
                    rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articlePostsDict["pubDates"][0] + "', proovime alternatiivi...", 0)
                    articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/text()[2]')
                    if len(articlePostsDict["pubDates"][0]) < 5:
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articlePostsDict["pubDates"][0] + "'", 0)
                    else:
                        rss_print.print_debug(__file__, "hangitud aeg[0]: '" + articlePostsDict["pubDates"][0] + "'", 4)
                if not articlePostsDict["pubDates"]:
                    rss_print.print_debug(__file__, "ei suutnud hankida ühtegi aega", 0)

            # teema postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlePostsDict["urls"], maxArticlePosts):
                # author
                articleDataDict["authors"] = parsers_common.list_add(articleDataDict["authors"], j, parsers_common.get(articlePostsDict["authors"], j))

                # description
                curArtDesc = parsers_common.get(articlePostsDict["descriptions"], j)
                curArtDesc = curArtDesc.replace('</div><div class="quotecontent">', '<br>')
                curArtDesc = parsers_common.fix_quatation_tags(curArtDesc, '<div class="quotetitle">', "</div>", "<blockquote>", "</blockquote>")
                articleDataDict["descriptions"] = parsers_common.list_add(articleDataDict["descriptions"], j, curArtDesc)

                # pubDates
                curArtPubDate = parsers_common.get(articlePostsDict["pubDates"], j)
                curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
                curArtPubDate = parsers_datetime.remove_weekday_strings(curArtPubDate)
                curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "eile", "%d %m %Y", offsetDays=-1)
                curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "täna", "%d %m %Y", offsetDays=0)
                curArtPubDate = parsers_datetime.guess_datetime(curArtPubDate)
                articleDataDict["pubDates"] = parsers_common.list_add(articleDataDict["pubDates"], j, curArtPubDate)

                # title
                curArtTitle = parsers_common.get(parentPages["titles"], i)
                curArtTitle = parsers_common.str_title_at_domain(curArtTitle, domain)
                articleDataDict["titles"] = parsers_common.list_add(articleDataDict["titles"], j, curArtTitle)

                # url
                curArtUrl = parsers_common.get(articlePostsDict["urls"], j)
                curArtUrl = parsers_common.link_add_end(curArtUrl, articlePostsDict["urls"][j])
                articleDataDict["urls"] = parsers_common.list_add(articleDataDict["urls"], j, curArtUrl)

                rss_print.print_debug(__file__, "teema " + str(i + 1) + " postitus nr. " + str(j + 1) + "/(" + str(len(articlePostsDict["urls"])) + ") on " + articlePostsDict["urls"][j], 2)

    return articleDataDict
