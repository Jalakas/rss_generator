
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@id="t-content"]/table[1]/tr', parent=True)
    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@id="t-content"]/table[1]/tr/td[1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@id="t-content"]/table[1]/tr/td[@class="left"]/b/a/@href')

    # remove unwanted content: descriptions
    dictList = ["Tartu"]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "not in", "descriptions")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "29.08.19" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d.%m.%y")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
