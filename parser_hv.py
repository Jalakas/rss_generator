
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//span[@class="title svelte-1izy135"]/text()')
    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//img[@class="svelte-1izy135"]/@src')
    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//a[@class="svelte-1izy135"]/@title')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//span[@class="title svelte-1izy135"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//a[@class="svelte-1izy135"]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "Kolmapäev, 29. juuni 2022 11:26:07 [Tanel]" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = curArtPubDate.split(',')[-1]
        curArtPubDate = curArtPubDate.split(' [')[0]
        curArtPubDate = parsers_datetime.months_to_int(curArtPubDate)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%d. %m %Y %H:%M:%S")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
