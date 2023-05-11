
import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 3)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    version = 0

    if "hinnavaatlus.ee" in domain:
        version = 1
        parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//div[@class="items body-main svelte-ma7jsj"]/a/span[1]/span[1]/text()')
        parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="items body-main svelte-ma7jsj"]/a/span[1]/text()')
        parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="items body-main svelte-ma7jsj"]/a/@href')
    else:
        parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl/dd[@class="posts"]/text()')
        parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl//a[@class="topictitle"]/text()')
        parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//ul[2]/li/dl//a[@class="topictitle"]/@href')

    # remove unwanted content: titles
    dictFilters = (
        "AMD",
        "Apple",
        "Assassin",
        "Batman",
        "Battlefield",
        "Call of Duty",
        "Cyberpunk",
        "Diablo 2",
        "Dying",
        "ELDEN RING",
        "Elisa",
        "Euro Truck",
        "Evil",
        "FIFA",
        "Far Cry",
        "Forza",
        "Galaxy",
        "Grand Theft",
        "IPhon",
        "Intel",
        "Kindle",
        "Lost Ark",
        "MMORPG",
        "MSI",
        "MacBook",
        "MacOS",
        "Mafia",
        "Mass Effect",
        "Meizu",
        "Minecraft",
        "Nintendo",
        "PS4",
        "Pixel",
        "PlayStation",
        "Steam",
        "Tanks",
        "Ukraina",
        "Vene-",
        "Venemaa",
        "Vidia",
        "War Thunder",
        "Watercool",
        "Windows",
        "Xbox",
        "arvutikast",
        "exile",
        "foorumiga seotud",
        "ipad",
        "konsool",
        "korpust",
        "moderaatorite",
        "seotud vead",
        "siia lingid",
        "toiteplok",
    )
    parentPages = parsers_common.article_data_dict_clean(__file__, parentPages, dictFilters, "in", "titles")

    if not parentPages["urls"] and "arutelud.com" in domain:
        rss_print.print_debug(__file__, "aktiivseid teemasid ei leitud, arutelude foorumis külastame mammutteemat", 1)
        parentPages["stamps"] = parsers_common.list_add_or_assign(parentPages["stamps"], 0, "")
        parentPages["titles"] = parsers_common.list_add_or_assign(parentPages["titles"], 0, "Mõtisklused makromajandusest, kinnisvarast ja muust")
        parentPages["urls"] = parsers_common.list_add_or_assign(parentPages["urls"], 0, "https://arutelud.com/viewtopic.php?t=4")

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            curParentUrl = parsers_common.get(parentPages["urls"], i)
            curParentUrl = curParentUrl.split("&sid=")[0]
            curParentUrl = curParentUrl + "&start=1000000"

            parentPagesStamp = parsers_common.get(parentPages["stamps"], i)
            parentPagesStamp = parentPagesStamp.split("/")[0]

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curParentUrl, cache='cacheStamped', pageStamp=parentPagesStamp)

            articlePostsDict = {}
            if version in {1}:
                rss_print.print_debug(__file__, "kasutame spetsiifilist hankimist " + str(version) + ", domain = " + domain, 2)
                articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[1]/span[@class="name"]/b/a/text()')
                articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[3]/td/span[@class="postbody"][1]', parent=True)
                articlePostsDict["descriptions2"] = parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[3]/td/span[@class="postbody"][2]', parent=True)
                articlePostsDict["descriptions3"] = parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[3]/td/table', parent=True)
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[1]/td/span[@class="postdetails"]/span[@class="postdetails"][1]/text()[1]')
                articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[1]/td/span[@class="postdetails"]/a/@href')
            else:
                rss_print.print_debug(__file__, "kasutame üldist hankimist, domain = " + domain, 3)
                articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]//strong//text()')
                articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@class="postbody"]//div[@class="content"]', parent=True)
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/time/@datetime')
                if not articlePostsDict["pubDates"]:
                    # arutelud, filmiveeb
                    articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/text()[2]')
                if not articlePostsDict["pubDates"]:
                    # cbradio, digitv, matkafoorum, vwklubi
                    articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/text()[1]')
                articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//p[@class="author"]/a/@href')

            # teema postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlePostsDict["urls"], maxArticlePosts):
                # author
                curArtAuthor = parsers_common.get(articlePostsDict["authors"], j)
                articleDataDict["authors"] = parsers_common.list_add(articleDataDict["authors"], j, curArtAuthor)

                # description
                curArtDesc = parsers_common.get(articlePostsDict["descriptions"], j)
                if not curArtDesc and version in {1}:
                    curArtDesc = parsers_common.get(articlePostsDict["descriptions2"], j)
                if not curArtDesc and version in {1}:
                    curArtDesc = parsers_common.get(articlePostsDict["descriptions3"], j)
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
