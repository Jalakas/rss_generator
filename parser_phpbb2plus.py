
import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 3)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    # version: phpBB2 Plus based on phpBB
    parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//td[@align="right"]/span[@class="gensmall"]/a[1]/@href')
    parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//a[@class="topictitle"]/text()')
    parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//a[@class="topictitle"]/@href')

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            curParentUrl = parsers_common.get(parentPages["urls"], i)
            curParentUrl = parsers_common.str_domain_url(domain, curParentUrl)

            parentPagesStamp = parsers_common.get(parentPages["stamps"], i)
            parentPagesStamp = curParentUrl.split("#")[-1]

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curParentUrl, cache='cacheStamped', pageStamp=parentPagesStamp)

            articlePostsDict = {}
            articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td/span/strong/a/text()')
            articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//table//tr/td[@class="postbody"]', parent=True)
            articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//td[@class="postdetails"]', parent=True)
            articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//td[@class="postdetails"]/a/@href')

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
                curArtPubDate = curArtPubDate.lower()
                curArtPubDate = curArtPubDate.split('<span>postituse')[0]
                curArtPubDate = curArtPubDate.split("postitatud: ")[1]
                curArtPubDate = curArtPubDate.replace("<strong>", "")
                curArtPubDate = curArtPubDate.replace("</strong>", "")
                curArtPubDate = curArtPubDate.replace(" kell ", ", ")
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
                curArtUrl = parsers_common.str_domain_url(domain, curArtUrl)
                articleDataDict["urls"] = parsers_common.list_add(articleDataDict["urls"], j, curArtUrl)

                rss_print.print_debug(__file__, "teema " + str(i + 1) + " postitus nr. " + str(j + 1) + "/(" + str(len(articlePostsDict["urls"])) + ") on " + articlePostsDict["urls"][j], 2)

    return articleDataDict
