
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="grid-main--item "]/div/div[2]/div[1]/h6/a[1]/text()')
    articleDataDict["urls"] =   parsers_common.xpath_to("list", pageTree, '//div[@class="grid-main--item "]/div/div[2]/div[1]/h6/a[1]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # titles
        curArtTitle = parsers_common.get(articleDataDict["titles"], i)
        curArtTitle = parsers_common.str_remove_clickbait(curArtTitle)
        articleDataDict["titles"] = parsers_common.list_add_or_assign(articleDataDict["titles"], i, curArtTitle)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # author
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '//span[@class="author"]/text()')
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description
            curArtDesc1 = parsers_common.xpath_to("single", pageTree, '//div[@class="page-layout--block"][1]/div[@class="page-layout--content"]/div[@class="page-layout--inner"]/div[@class="article-main--content article-main--excerpt formatted--content"]', parent=True)
            if not curArtDesc1:
                curArtDesc1 = parsers_common.xpath_to("single", pageTree, '//div[@class="page-layout--content"]/div[@class="page-layout--inner"]/div[@class="article-main--content article-main--excerpt formatted--content"]', parent=True)

            curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@class="page-layout--block"][2]/div[@class="page-layout--content"]/div[@class="page-layout--inner"]', parent=True, multi=True)

            curArtDesc = curArtDesc1 + curArtDesc2
            curArtDesc = curArtDesc.split("Edasi lugemiseks")[0]
            curArtDesc = curArtDesc.split("Jaga:")[0]
            curArtDesc = curArtDesc.split("Samal teemal")[0]
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # image
            curArtImg = parsers_common.xpath_to("single", pageTree, '//div[@class="page-layout--block"][1]//div[@class="image-gallery-image first-in-gallery"][1]/picture[1]/img[@class="article-image"]/@src')
            if not curArtImg:
                curArtImg = parsers_common.xpath_to("single", pageTree, '//div[@class="part"][1]/div/p/img/@src')
            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

            # pubDates from "täna 16:53" to datetime()
            curArtPubDate = parsers_common.xpath_to("single", pageTree, '//div[@class="details--inner"]/text()')
            curArtPubDate = curArtPubDate.split(",")[-1]
            curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "eile", "%d. %m %Y ", offsetDays=-1)
            curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "täna", "%d. %m %Y ", offsetDays=0)
            curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d. %m %Y %H:%M")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
