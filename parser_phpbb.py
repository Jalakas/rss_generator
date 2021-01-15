#!/usr/bin/env python3

import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    maxArticleBodies = min(rss_config.MAX_ARTICLE_BODIES, 10)
    maxArticlePostsCount = round(rss_config.MAX_ARTICLE_BODIES / maxArticleBodies)  # set 0 for all posts

    if "militaar.net" in domain:
        articlesTitles = parsers_common.xpath_to_list(pageTree, '//tr[@valign="middle"]/td[3]/a/text()')
        articlesUrls = parsers_common.xpath_to_list(pageTree, '//tr[@valign="middle"]/td[3]/a/@href')
    else:
        articlesTitles = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[@class="topictitle"]/text()')
        articlesUrls = parsers_common.xpath_to_list(pageTree, '//div[@class="inner"]/ul/li/dl/dt/div/a[@class="topictitle"]/@href')

    if not articlesUrls:
        if "arutelud.com" in domain:
            rss_print.print_debug(__file__, "aktiivseid teemasid ei leitud, arutelude foorumis külastame mammutteemat", 1)
            articlesTitles.append("Arutelud")
            articlesUrls.append("http://arutelud.com/viewtopic.php?f=3&t=4&sd=d&sk=t&st=7")
        else:
            rss_print.print_debug(__file__, "ei leidnud teemade nimekirjast ühtegi aktiivset teemat", 0)

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlesUrls):
        # teemalehe sisu hankimine
        if (rss_config.GET_ARTICLE_BODIES is True and i < maxArticleBodies):
            articlesUrls[i] = articlesUrls[i].split("&sid=")[0]
            pageTree = parsers_common.get_article_tree(session, domain, articlesUrls[i] + "&start=100000", noCache=True)

            if "militaar.net" in domain:
                articlesPostsAuthors = parsers_common.xpath_to_list(pageTree, '//tr/td/b[@class="postauthor"]/text()')
                articlesPostsPubDates = parsers_common.xpath_to_list(pageTree, '//tr/td[@class="gensmall"]/div[2]/text()')
                articlesPostsUrls = parsers_common.xpath_to_list(pageTree, '//tr/td[@class="gensmall"]/div[2]/a/@href')
                articlesPostsDescriptions = parsers_common.xpath_to_list(pageTree, '//tr/td/div[@class="postbody"][1]', parent=True)
            else:
                articlesPostsAuthors = parsers_common.xpath_to_list(pageTree, '//p[@class="author"]//strong//text()')
                articlesPostsPubDates = parsers_common.xpath_to_list(pageTree, '//p[@class="author"]/text()[1]')
                articlesPostsUrls = parsers_common.xpath_to_list(pageTree, '//p[@class="author"]/a/@href')
                articlesPostsDescriptions = parsers_common.xpath_to_list(pageTree, '//div[@class="content"]', parent=True)

            if articlesPostsUrls:
                if not articlesPostsPubDates:
                    rss_print.print_debug(__file__, "ei suutnud hankida ühtegi aega", 0)
                else:
                    if len(str(articlesPostsPubDates[0])) < 5:
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articlesPostsPubDates[0] + "', proovime alternatiivi...", 1)
                        articlesPostsPubDates = parsers_common.xpath_to_list(pageTree, '//p[@class="author"]/text()[2]')
                    # proovime uuesti
                    if len(str(articlesPostsPubDates[0])) < 5:
                        rss_print.print_debug(__file__, "hangitud aeg[0] liiga lühike: '" + articlesPostsPubDates[0] + "'", 0)
                    else:
                        rss_print.print_debug(__file__, "hangitud aeg[0]: '" + articlesPostsPubDates[0] + "'", 4)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlesPostsUrls, maxArticlePostsCount):
                # author
                curArtAuthor = articlesPostsAuthors[j]
                articleDataDict["authors"].append(curArtAuthor)

                # description
                curArtDesc = articlesPostsDescriptions[j]
                if "militaar.net" in domain:
                    curArtDesc = curArtDesc.replace('</div><div class="quotecontent">', '<br>')
                    curArtDesc = parsers_common.fix_quatation_tags(curArtDesc, '<div class="quotetitle">', "</div>", "<blockquote>", "</blockquote>")

                curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
                articleDataDict["descriptions"].append(curArtDesc)

                # datetime
                curArtPubDate = articlesPostsPubDates[j]
                curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
                curArtPubDate = parsers_common.remove_weekday_strings(curArtPubDate)
                curArtPubDate = parsers_datetime.guess_datetime(curArtPubDate)
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                curArtTitle = parsers_common.title_at_domain(articlesTitles[i], domain)
                articleDataDict["titles"].append(curArtTitle)

                # url
                curArtUrl = articlesPostsUrls[j]
                curArtUrl = curArtUrl.split("&sid=")[0]
                if "#" not in curArtUrl:
                    rss_print.print_debug(__file__, "lisame lingi lõppu puuduva:" + "#" + articlesPostsUrls[j].split("#")[1], 0)
                    curArtUrl = curArtUrl + "#" + articlesPostsUrls[j].split("#")[1]
                articleDataDict["urls"].append(curArtUrl)

                rss_print.print_debug(__file__, "teema postitus nr. " + str(j + 1) + "/(" + str(len(articlesPostsUrls)) + ") on " + articlesPostsUrls[j], 2)

    # remove unwanted content
    dictBlacklist = ["jumal ", "Jumal "]
    dictCond = "in"
    dictField = "descriptions"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    return articleDataDict
