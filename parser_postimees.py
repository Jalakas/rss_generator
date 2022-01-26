
import parsers_common
import parsers_datetime
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="article-content"]/div[@class="article-content__meta"]/span[@class="article-content__date-published"]/text()')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="article-content"]/a[@class="article-content__headline"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="article-content"]/a[@class="article-content__headline"]/@href')

    articleDataDictPubDatesDay = parsers_common.xpath_to("list", pageTree, '//div[@class="article-content"]/div[@class="article-content__meta"]/span[@class="article-content__date-published"]/span/text()')

    # remove unwanted content: titles
    dictList = [
        "Sakala kuulutused",
        "Tartu Börs,",
        "positiivseid proove",
    ]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "titles")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "24.12.2017 17:51" to datetime()
        curArtPubDateDay = ""
        if len(articleDataDictPubDatesDay) - 1 >= i:
            curArtPubDateDay = parsers_common.get(articleDataDictPubDatesDay, i)
            curArtPubDateDay = parsers_datetime.replace_string_with_timeformat(curArtPubDateDay, "Eile", "%d.%m.%Y", offsetDays=-1)
            curArtPubDateDay = parsers_datetime.replace_string_with_timeformat(curArtPubDateDay, "Täna", "%d.%m.%Y", offsetDays=0)

        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDateDay + curArtPubDate, "%d.%m.%Y, %H:%M")
        articleDataDict["pubDates"][i] = curArtPubDate

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # author
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '//span[@class="article-authors__name"]/text()', multi=True)
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description1 - enne pilti
            curArtDesc1 = ""
            if not curArtDesc1:
                curArtDesc1 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--video"][1]', parent=True, count=True)
            if not curArtDesc1:
                curArtDesc1 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--articleBullets"]', parent=True, count=True)

            # description2 - pildi ja kuulamise vahel
            curArtDesc2 = ""
            if not curArtDesc2:
                curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@itemprop="articleBody"]', parent=True, count=True)
            if not curArtDesc2:
                curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"]', parent=True, count=True, multi=True)
            if not curArtDesc2:
                curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//span[@class="figure__caption--title"][1]', parent=True, count=True)
            if not curArtDesc2:
                curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body--first-child article-body__item--lead"]', parent=True, count=True)
            if not curArtDesc2:
                curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@itemprop="description"]', parent=True, count=True)

            # description3 - pärast kuulamist
            curArtDesc3 = ""
            if not curArtDesc3:
                curArtDesc3 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--htmlElement"]', parent=True, count=True, multi=True)
            if not curArtDesc3:
                curArtDesc3 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--premium-indicator"]', parent=True, count=True)

            # description4 - hall väljajuhatus
            curArtDesc4 = ""
            if not curArtDesc4:
                curArtDesc4 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body--teaser"]', parent=True, count=True)
            if not curArtDesc4:
                curArtDesc4 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--gallery"]', parent=True, count=True, multi=True)

            # image
            curArtImg = ""
            if not curArtImg:
                curArtImg = parsers_common.xpath_to("single", pageTree, '//div[@class="article-superheader article-superheader--figure"]/div[@class="article-superheader__background"]/@style', count=True)
                curArtImg = curArtImg.split("url('")[-1].strip("');")
            if not curArtImg:
                curArtImg = parsers_common.xpath_to("single", pageTree, '//figure[@class="figure"]/img[@class="figure--has-fullscreen"]/@src', count=True)
            if not curArtImg:
                curArtImg = parsers_common.xpath_to("single", pageTree, '//meta[@property="og:image"]/@content', count=True)

            # kontrollid
            if "-kuulutused-" in curArtUrl:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: kuulutused", 2)
            elif "-karikatuur" in curArtUrl:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: karikatuur", 2)
            else:
                if not curArtDesc1:
                    rss_print.print_debug(__file__, "1. plokk on tühi. (Pildieelne loendiplokk puudub?)", 2)
                else:
                    rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc1, 4)
                if not curArtDesc2:
                    rss_print.print_debug(__file__, "2. plokk on tühi. (Pildi ja kuulamise vahe plokk puudub?) - " + curArtUrl, 0)
                else:
                    rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 4)
                if not curArtDesc3:
                    rss_print.print_debug(__file__, "3. plokk on tühi. (Pärast kuulamist plokk puudub?)", 0)
                else:
                    rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 4)
                if not curArtDesc4:
                    if "button--for-subscription" in curArtDesc3:
                        curArtDesc3 = curArtDesc3.split('<span class="button--for-subscription')[0]
                        rss_print.print_debug(__file__, "4. plokk on tühi. (Kolmandas plokis oli teemant)", 3)
                    else:
                        rss_print.print_debug(__file__, "4. plokk on tühi. (Hall fadeout plokk puudub?)", 2)
                else:
                    rss_print.print_debug(__file__, "curArtDesc4 = " + curArtDesc4, 4)
                if not curArtImg:
                    rss_print.print_debug(__file__, "pilti ei leitud.", 0)
                else:
                    rss_print.print_debug(__file__, "curArtImg = " + curArtImg, 4)

                if curArtDesc1 and curArtDesc1 == curArtDesc2:
                    rss_print.print_debug(__file__, "1. ja 2. plokk langevad kokku", 0)
                    rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc1, 1)
                    rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 1)
                if curArtDesc2 and curArtDesc2 == curArtDesc3:
                    rss_print.print_debug(__file__, "2. ja 3. plokk langevad kokku", 0)
                    rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 1)
                    rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 1)
                if curArtDesc3 and curArtDesc3 == curArtDesc4:
                    rss_print.print_debug(__file__, "3. ja 4. plokk langevad kokku", 0)
                    rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 1)
                    rss_print.print_debug(__file__, "curArtDesc4 = " + curArtDesc4, 1)
                if curArtDesc4 and curArtDesc4 == curArtDesc1:
                    rss_print.print_debug(__file__, "4. ja 1. plokk langevad kokku", 0)
                    rss_print.print_debug(__file__, "curArtDesc4 = " + curArtDesc3, 1)
                    rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc4, 1)

            curArtDesc = curArtDesc1 + ' ' + curArtDesc2 + ' ' + curArtDesc3 + ' ' + curArtDesc4

            if "button--for-subscription" in curArtDesc:
                curArtDesc = curArtDesc.replace(' tellijatele', '')
                curArtDesc = curArtDesc.replace('<a href="https://minumeedia.postimees.ee/kampaania/" target="_blank" class="my-media-link">digipaketi</a>', '')
                curArtDesc = curArtDesc.replace('<div class="article-body__item article-body__item--audio-teaser">', '<div>')
                curArtDesc = curArtDesc.replace('<div class="audio-teaser">', '<div>')
                curArtDesc = curArtDesc.replace('<img data-lazy-src="/v5/img/icons/diamond-black-on-yellow.svg" alt="Tellijale" src="/v5/img/icons/diamond-black-on-yellow.svg" width="30" height="30">', "")
                curArtDesc = curArtDesc.replace('<img src="/v5/img/icons/diamond-black-on-yellow.svg" alt="Tellijale" width="30" height="30">', "")
                curArtDesc = curArtDesc.replace('<span class="button--for-subscription">', "<span>")
                curArtDesc = curArtDesc.replace('<span class="button--for-subscription__diamond diamond--ee">', "<span>")
                curArtDesc = curArtDesc.replace('<span class="button--for-subscription__text"', "")
                curArtDesc = curArtDesc.replace('Artikkel on kuulatav', '')
                curArtDesc = curArtDesc.replace('Tellijale', '')

            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

    return articleDataDict
