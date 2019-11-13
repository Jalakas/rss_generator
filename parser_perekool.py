#!/usr/bin/env python3

import parsers_common
import parsers_datetime
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    maxArticleBodies = min(rss_config.MAX_ARTICLE_BODIES, 5)
    maxArticlePostsCount = round(150 / maxArticleBodies)  # set 0 for all posts

    articlesTitles = parsers_common.xpath_to_list(pageTree, '//tr/th[@class="col-7 teemapealkiri"]/a/text()')
    articlesUrls = parsers_common.xpath_to_list(pageTree, '//tr/th[@class="col-4"]/a/@href')

    if not articlesUrls:
        rss_print.print_debug(__file__, "ei leidnud teemade nimekirjast ühtegi aktiivset teemat", 0)

    # teemade läbivaatamine
    for i in parsers_common.article_urls_range(articlesUrls):
        # teemalehe sisu hankimine
        if (rss_config.GET_ARTICLE_BODIES is True and i < maxArticleBodies):
            articlesUrls[i] = articlesUrls[i].split("/#")[0]

            pageTree = parsers_common.get_article_tree(session, domain, articlesUrls[i], noCache=True)

            # articlesPostsAuthors = parsers_common.xpath_to_list(pageTree, '//div[@class="fn n"]/text()')
            articlesPostsPubDatetime = parsers_common.xpath_to_list(pageTree, '//div[@class="post_date date updated"]/text()')
            articlesPostsUrls = parsers_common.xpath_to_list(pageTree, '//div[@class="bbp-reply-header entry-title"]/@id')
            articlesPostsDescriptions = parsers_common.xpath_to_list(pageTree, '//div[@class="bbp-reply-content entry-content"]', parent=True)

            # postituste läbivaatamine
            for j in parsers_common.article_posts_range(articlesPostsUrls, maxArticlePostsCount):
                # description
                curArtDesc = articlesPostsDescriptions[j]
                curArtDesc = curArtDesc.split('<div class="gdrts-dynamic-block')[0]
                curArtDesc = parsers_common.fix_drunk_post(curArtDesc)
                articleDataDict["descriptions"].append(curArtDesc)

                # datetime
                curArtPubDate = articlesPostsPubDatetime[j]
                curArtPubDate = parsers_datetime.guess_datetime(curArtPubDate)
                articleDataDict["pubDates"].append(curArtPubDate)

                # title
                curArtTitle = parsers_common.title_at_domain(articlesTitles[i], domain)
                articleDataDict["titles"].append(curArtTitle)

                # url
                curArtUrl = articlesUrls[i] + "/#" + articlesPostsUrls[j]
                articleDataDict["urls"].append(curArtUrl)

                rss_print.print_debug(__file__, "teema postitus nr. " + str(j + 1) + "/(" + str(len(articlesPostsUrls)) + ") on " + articlesPostsUrls[j], 2)

    # remove unwanted content
    dictBlacklist = ["abort", "beebi", "IVF", " rased", "rasest", "räpp", "triibupüüdjad"]
    dictCond = "in"
    dictField = "titles"
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictField, dictCond, dictBlacklist=dictBlacklist)

    return articleDataDict
