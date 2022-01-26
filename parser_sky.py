
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="box-news-block-title "]/a[@title]/@title')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="box-news-block-title "]/a[@title]/@href')

    # remove unwanted content: urls
    dictList = ["https://sky.ee/rock-fmi-hommikuprogramm-igal-toopaeval-kell-7-10/"]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "urls")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # author
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '//div[@class="post-content"]/div[@class="article-page-author"]/p/text()')
            if ": " in curArtAuthor:
                curArtAuthor = curArtAuthor.split(": ")[1]
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description
            curArtDesc1 = parsers_common.xpath_to("single", pageTree, '//div[@class="posts"]/div[@class="two-side-content-container clearfix"][1]//div[@class="post-content"]/strong/p/text()')
            curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@class="posts"]/div[@class="two-side-content-container clearfix"][2]//div[@class="post-content"]', parent=True)
            curArtDesc = curArtDesc1 + curArtDesc2
            if '<p class="related-cta">LOE KA NEID UUDISEID!</p>' in curArtDesc:
                curArtDesc = curArtDesc.split('<p class="related-cta">LOE KA NEID UUDISEID!</p>')[0]
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
