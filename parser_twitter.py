
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["authors"] =      parsers_common.xpath_to("list", pageTree, '//section/div/div/div/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/a/div/div[1]/div[1]/span/span/text()')
    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//section/div/div/div/div/div/article/div/div/div/div[2]/div[2]/div[2]/div[1]/div/span[1]', parent=True)
    articleDataDict["pubDates"] =     parsers_common.xpath_to("list", pageTree, '//section/div/div/div/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a/time/@datetime')
    articleDataDict["titles"] =       parsers_common.xpath_to("list", pageTree, '//section/div/div/div/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/a/div/div[1]/div[1]/span/span/text()')
    articleDataDict["urls"] =         parsers_common.xpath_to("list", pageTree, '//section/div/div/div/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates 2021-02-12T16:08:02.000Z
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dT%H:%M:%S.000Z")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

        # title
        curArtTitle = parsers_common.get(articleDataDict["titles"], i)
        curArtTitle = parsers_common.str_title_at_domain(curArtTitle, domain)
        articleDataDict["titles"] = parsers_common.list_add_or_assign(articleDataDict["titles"], i, curArtTitle)

    return articleDataDict
