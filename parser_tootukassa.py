
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/p', parent=True)
    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="right-content"]/div[@class="application-date"][1]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="applied-jobs"]/div/div[@class="job-content"]/div[@class="left-content"]/h2/a/@href')

    # remove unwanted content: descriptions
    dictList = [
        "jurist",
        "logopeed",
        "pedagoog",
        "psühholoog",
        "raamatupidaja",
        "sotsiaal",
        "õpetaja",
    ]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "titles")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "Avaldatud: 12.12.2017" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = curArtPubDate.split(': ')[1]
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d.%m.%Y")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

        # url
        curArtUrl = parsers_common.get(articleDataDict["urls"], i)
        curArtUrl = curArtUrl.split('?ref=')[0]
        articleDataDict["urls"] = parsers_common.list_add_or_assign(articleDataDict["urls"], i, curArtUrl)

    return articleDataDict
