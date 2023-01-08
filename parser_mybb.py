
import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    maxArticleBodies = min(rss_config.REQUEST_ARTICLE_BODIES_MAX, 5)
    maxArticlePosts = round(rss_config.REQUEST_ARTICLE_POSTS_MAX / maxArticleBodies)  # set 0 for all posts

    parentPages = {}
    parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//div[@data-lang="Vastuseid"]/a/text()')
    if not parentPages["stamps"]:
        parentPages["stamps"] = parsers_common.xpath_to("list", pageTree, '//div[@class="threadbit_stats align_right smalltext"]/span[1]/text()')
    parentPages["titles"] = parsers_common.xpath_to("list", pageTree, '//span[@class=" subject_old"]/a/text()')
    parentPages["urls"] = parsers_common.xpath_to("list", pageTree, '//span[@class=" subject_old"]/a/@href')

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(parentPages["urls"]):
        # teemalehe sisu hankimine
        if parsers_common.should_get_article_body(i, maxArticleBodies):
            curParentUrl = parsers_common.get(parentPages["urls"], i)
            curParentUrl = curParentUrl.split("&sid=")[0]
            curParentUrl = curParentUrl + "&page=-1"
            curParentUrl = parsers_common.str_domain_url(domain, curParentUrl)
            parentPagesStamp = parsers_common.get(parentPages["stamps"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curParentUrl, cache='cacheStamped', pageStamp=parentPagesStamp)

            articlePostsDict = {}
            articlePostsDict["authors"] = parsers_common.xpath_to("list", pageTree, '//div[starts-with(@class,"author_information")]/strong/span[@class="largetext"]/a/text()')
            articlePostsDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@class="post_body scaleimages"]', parent=True)
            articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="post_head"]/span[@class="post_date"]/span[@class!="post_edit"]/@title')
            if not articlePostsDict["pubDates"]:
                articlePostsDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="post_head"]/span[@class="post_date"]/text()')
            articlePostsDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="post_head"]/div/strong/a/@href')

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
                if "tund" in curArtPubDate:
                    curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, curArtPubDate, "%d-%m-%y, %H:%M", offsetHours=curArtPubDate.split(" ")[0])
                elif "minut" in curArtPubDate:
                    curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, curArtPubDate, "%d-%m-%y, %H:%M", offsetMinutes=curArtPubDate.split(" ")[0])
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
