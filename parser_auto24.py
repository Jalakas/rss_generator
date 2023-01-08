
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["authors"] = parsers_common.xpath_to("list", pageTree, '//div[@class="message"]/div[@class="name"]', parent=True)
    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//div[@class="message"]/div[@class="content"]', parent=True)
    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="message"]/div[@class="posttime"]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="message"]/div[@class="title"]/a[3]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="message"]/div[@class="title"]/a[3]/@href')

    # remove unwanted content: titles
    dictFilters = (
        "Kaebused",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # description
        curArtDesc = parsers_common.get(articleDataDict["descriptions"], i)
        curArtDesc = curArtDesc.split('<div class="userControls')[0]
        articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

        # title
        curArtTitle = parsers_common.get(articleDataDict["titles"], i)
        curArtTitle = parsers_common.str_lchop(curArtTitle, "Re: ")
        curArtTitle = parsers_common.str_title_at_domain(curArtTitle, domain)
        articleDataDict["titles"] = parsers_common.list_add_or_assign(articleDataDict["titles"], i, curArtTitle)

        # pubDates magic from "20:22 01.09.2019" to Datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "eile", "%d.%m.%Y", offsetDays=-1)
        curArtPubDate = parsers_datetime.replace_string_with_timeformat(curArtPubDate, "täna", "%d.%m.%Y", offsetDays=0)
        curArtPubDate = parsers_datetime.add_missing_date_to_string(curArtPubDate, "%H:%M %d.%m.%Y", " %d.%m.%Y")
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%H:%M %d.%m.%Y")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

    return articleDataDict
