
import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 4)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    version = 0
    if "kipper.ee" in domain:  # old version
        version = 1
        parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td//p[@class="topicdetails"]/text()')
        parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td//a[@class="topictitle"]/text()')
        parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td//a[@class="topictitle"]/@href')
    elif "pingviin.org" in domain:  # old version: phpBB2 Plus based on phpBB
        version = 2
        parentPages["stamps"] = ""
        parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//table/tr/td/span/a[@class="topictitle"]/text()')
        parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//table/tr/td/span/a[@class="topictitle"]/@href')
    else:
        parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl/dd[@class="posts"]/text()')
        parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl/*/div/a[@class="topictitle"]/text()')
        parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl/*/div/a[@class="topictitle"]/@href')

    if not parentPages["urls"] and "arutelud.com" in domain:
        rss_print.print_debug(__file__, "aktiivseid teemasid ei leitud, arutelude foorumis külastame mammutteemat", 1)
        parentPages["stamps"] = parsers_common.list_add_or_assign(parentPages["stamps"], 0, "")
        parentPages["titles"] = parsers_common.list_add_or_assign(parentPages["titles"], 0, "Arutelud")
        parentPages["urls"] = parsers_common.list_add_or_assign(parentPages["urls"], 0, "https://arutelud.com/viewtopic.php?f=3&t=4&sd=d&sk=t&st=7")

    # remove unwanted content: titles
    dictFilters = (
        "Race.Fi:",
    )
    parentPages = parsers_common.article_data_dict_clean(__file__, parentPages, dictFilters, "in", "titles")

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            curParentUrl = parsers_common.get(parentPages["urls"], i)
            curParentUrl = curParentUrl.split("&sid=")[0]
            curParentUrl = curParentUrl + "&start=1000000"
            parentPagesStamp = parsers_common.get(parentPages["stamps"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curParentUrl, cache='cacheStamped', pageStamp=parentPagesStamp)

            articlePostsDict = {}
            if version in {1}:
                rss_print.print_debug(__file__, "kasutame spetsiifilist hankimist 1, domain = " + domain, 2)
                articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//tr/td/b[@class="postauthor"]/text()')
                articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//tr/td/div[@class="postbody"][1]', parent=True)
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//tr/td[@class="gensmall"]/div[@style="float: right;"]/text()')
                articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//tr/td[@class="gensmall"]/div[@style="float: right;"]/a/@href')
            elif version in {2}:
                rss_print.print_debug(__file__, "kasutame spetsiifilist hankimist 2, domain = " + domain, 2)
                articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td/span/strong/a/text()')
                articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td[@class="postbody"]', parent=True)
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td[@class="postdetails"]/text()')
                articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td[@valign="top"]/a[1]/@href')
            else:
                rss_print.print_debug(__file__, "kasutame üldist hankimist, domain = " + domain, 3)
                articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]//strong//text()')
                articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@class="postbody"]/div/div[@class="content"]', parent=True)
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/time/@datetime')
                articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/a/@href')

            if not articlePostsDict["pubDates"]:
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/time/text()')
            if not articlePostsDict["pubDates"]:
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/text()[1]')
            if articlePostsDict["pubDates"] and len(articlePostsDict["pubDates"][0]) < 5:
                rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articlePostsDict["pubDates"][0] + "', proovime alternatiivi...", 1)
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/text()[2]')
                if articlePostsDict["pubDates"] and len(articlePostsDict["pubDates"][0]) < 5:
                    rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articlePostsDict["pubDates"][0] + "'", 0)
                else:
                    rss_print.print_debug(__file__, "hangitud aeg[0]: '" + articlePostsDict["pubDates"][0] + "'", 4)
            if not articlePostsDict["pubDates"]:
                rss_print.print_debug(__file__, "ei suutnud hankida ühtegi aega", 0)

            # teema postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlePostsDict["urls"], maxArticlePosts):
                # author
                curArtAuthor = parsers_common.get(articlePostsDict["authors"], j)
                articleDataDict["authors"] = parsers_common.list_add(articleDataDict["authors"], j, curArtAuthor)

                # description
                curArtDesc = parsers_common.get(articlePostsDict["descriptions"], j)
                curArtDesc = curArtDesc.replace('</div><div class="quotecontent">', '<br>')
                curArtDesc = parsers_common.fix_quatation_tags(curArtDesc, '<div class="quotetitle">', "</div>", "<blockquote>", "</blockquote>")
                articleDataDict["descriptions"] = parsers_common.list_add(articleDataDict["descriptions"], j, curArtDesc)

                # pubDates
                curArtPubDate = parsers_common.get(articlePostsDict["pubDates"], j)
                curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
                curArtPubDate = parsers_datetime.remove_weekday_strings(curArtPubDate)
                curArtPubDate = curArtPubDate.lstrip("etknrlp ")
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
