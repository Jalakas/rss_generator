
import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 5)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//div[@class="tabs-content tab-active shadow"]/ul[@class="adds-list list"]/li[@class="adds-list-item"]/a[h3/@class="adds-list-title"]/h3[@class="adds-list-title"]/span[@class="adds-list-meta"]/text()')
    parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="tabs-content tab-active shadow"]/ul[@class="adds-list list"]/li[@class="adds-list-item"]/a[h3/@class="adds-list-title"]/h3[@class="adds-list-title"]/text()')
    parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="tabs-content tab-active shadow"]/ul[@class="adds-list list"]/li[@class="adds-list-item"]/a[h3/@class="adds-list-title"]/@href')

    # muudame suuna sobivaks
    parentPages = parsers_common.dict_reverse_order(parentPages)

    # remove unwanted content: titles
    dictList = [
        "AMD",
        "Apple",
        "Assassin",
        "Batman",
        "Battlefield",
        "Call of Duty",
        "Cyberpunk",
        "Diablo 2",
        "Dying",
        "Escape From Tarkov",
        "Euro Truck",
        "Evil",
        "FIFA",
        "Far Cry",
        "Forza",
        "Galaxy",
        "Grand Theft",
        "IPhon",
        "Kindle",
        "MMORPG",
        "MSI",
        "MacBook",
        "MacOS",
        "Mafia",
        "Mass Effect",
        "Meizu",
        "Minecraft",
        "Nintendo",
        "Pixel",
        "PlayStation",
        "Steam",
        "Tanks",
        "Vidia",
        "War Thunder",
        "Watercool",
        "Windows",
        "Xbox",
        "arvutikast",
        "exile",
        "foorumiga seotud",
        "konsool",
        "korpust",
        "moderaatorite",
        "seotud vead",
        "siia lingid",
        "toiteplok",
    ]
    parentPages = parsers_common.article_data_dict_clean(parentPages, dictList, "in", "titles")

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            parentPages["stamps"][i] = parentPages["stamps"][i].split("/")[0]
            parentPages["urls"][i] = parentPages["urls"][i].split("&sid=")[0]
            pageTree = parsers_common.get_article_tree(domain, parentPages["urls"][i], cache='cacheStamped', pageStamp=parentPages["stamps"][i])

            articlePostsDict = {}
            articlePostsDict["authors"] =       parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[1]/span[@class="name"]/b/a/text()')
            articlePostsDict["descriptions1"] = parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[3]/td/span[@class="postbody"][1]', parent=True)
            articlePostsDict["descriptions2"] = parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[3]/td/span[@class="postbody"][2]', parent=True)
            articlePostsDict["pubDates"] =      parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[1]/td/span[@class="postdetails"]/span[@class="postdetails"][1]/text()[1]')
            articlePostsDict["urls"] =          parsers_common.xpath_to("list", pageTree, '//table[@class="forumline"]/tr/td[2]/table/tr[1]/td/span[@class="postdetails"]/a/@href')

            # teema postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlePostsDict["urls"], maxArticlePosts):
                # author
                articleDataDict["authors"] = parsers_common.list_add(articleDataDict["authors"], j, parsers_common.get(articlePostsDict["authors"], j))

                # description
                curArtDesc = parsers_common.get(articlePostsDict["descriptions1"], j)
                if not curArtDesc:
                    curArtDesc = parsers_common.get(articlePostsDict["descriptions2"], j)
                curArtDesc = curArtDesc.replace('</div><div class="quotecontent">', '<br>')
                curArtDesc = parsers_common.fix_quatation_tags(curArtDesc, '<div class="quotetitle">', "</div>", "<blockquote>", "</blockquote>")
                articleDataDict["descriptions"] = parsers_common.list_add(articleDataDict["descriptions"], j, curArtDesc)

                # pubDates
                curArtPubDate = parsers_common.get(articlePostsDict["pubDates"], j)
                curArtPubDate = curArtPubDate[0:16]
                curArtPubDate = parsers_datetime.guess_datetime(curArtPubDate)  # 14.07.2020 07:59
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
