
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-cnt"]/div[@class="sb-article-prolog"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-image"]/@style')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/div[@class="sb-article-cnt"]/div[@class="sb-article-title"]/h3/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '/html/body/div[3]/div/div[1]/div[@class="sb-article"]/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # author
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '//div[@class="sg-article-details"]/div[@class="author"]/text()')
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '/html/body/div[3]/div/div[@class="page-content"]/div[@class="sg-article"]/div[@class="sg-article-text"]', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # pubDates magic from "18.08.2019 21:35" to datetime()
            curArtPubDate = parsers_common.xpath_to("single", pageTree, '//div[@class="sg-article-details"]/div[@class="date"]/text()')
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d.%m.%Y %H:%M")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
