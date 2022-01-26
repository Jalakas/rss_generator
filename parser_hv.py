
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/div/p', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/p/img/@src')
    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/@title')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/div/h3/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//ul[@class="news-list list"]/li/div[@class="inner"]/a[@class="news-list-link"]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "03.01.2018 11:09.08 [Tanel]" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = curArtPubDate.split('[')[0]
        curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d. %m %Y %H:%M:%S")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
