
import parsers_common
import parsers_datetime
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["authors"] = parsers_common.xpath_to("list", pageTree, '//div[@class="structured-content__block structured-content__block--column"]/article/meta[@itemprop="author"]/@content')
    articleDataDict["pubDates"] = parsers_common.xpath_to("list", pageTree, '//div[@class="structured-content__block structured-content__block--column"]/article/a/meta[@itemprop="datePublished"]/@content')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//div[@class="structured-content__block structured-content__block--column"]/article/a/div[@class="list-article__text"]/div[@class="list-article__text-content"]/h2/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//div[@class="structured-content__block structured-content__block--column"]/article/a/@href')

    # remove unwanted content: titles
    dictFilters = (
        "Kuulutused,",
        "Sakala kuulutused",
        "Tartu Börs,",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # description1 - bold sissejuhatus
            curArtDesc1 = ""
            if not curArtDesc1:
                curArtDesc1 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"]', parent=True, count=True, multi=True)

            # description3 - tavaline sisu
            curArtDesc2 = ""
            if not curArtDesc2:
                curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--htmlElement"]', parent=True, count=True, multi=True)
            if not curArtDesc2:
                curArtDesc2 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--highlightedContent"]', parent=True, count=True, multi=True)
            if not curArtDesc2:
                curArtDesc2 = parsers_common.xpath_to("single", pageTree, '(//span[@class="figure__caption--title"])[1]', parent=True, count=True)


            # description4 - hall väljajuhatus, vms
            curArtDesc3 = ""
            if not curArtDesc3:
                curArtDesc3 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body__item--teaser"]', parent=True, count=True)
            if not curArtDesc3:
                curArtDesc3 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--highlightedContent article-body__item--teaser"]', parent=True, count=True)
            if not curArtDesc3:
                curArtDesc3 = parsers_common.xpath_to("single", pageTree, '(//div[@class="article-body__item article-body__item--video"])[1]', parent=True, count=True)
            if not curArtDesc3:
                curArtDesc3 = parsers_common.xpath_to("single", pageTree, '//div[@class="article-body__item article-body__item--gallery"]', parent=True, count=True, multi=True)

            curArtDesc = curArtDesc1 + ' ' + curArtDesc2 + ' ' + curArtDesc3
            curArtDesc = curArtDesc.replace('<a href="https://minumeedia.postimees.ee/kampaania/" target="_blank" class="my-media-link">digipaketi</a>', '')
            curArtDesc = curArtDesc.replace('<div class="article-body__item article-body__item--audio-teaser">', '<div>')
            curArtDesc = curArtDesc.replace('<div class="audio-teaser">', '<div>')
            curArtDesc = curArtDesc.replace('<img data-lazy-src="/v5/img/icons/diamond-black-on-yellow.svg" alt="Tellijale" src="/v5/img/icons/diamond-black-on-yellow.svg" width="30" height="30">', "")
            curArtDesc = curArtDesc.replace('<img src="/v5/img/icons/diamond-black-on-yellow.svg" alt="Tellijale" width="30" height="30">', "")
            curArtDesc = curArtDesc.replace('<span class="button--for-subscription">', "<span>")  # 2022.02.15
            curArtDesc = curArtDesc.replace('<span class="button--for-subscription__diamond diamond--ee">', "<span>")  # 2022.02.15
            curArtDesc = curArtDesc.replace('<span class="button--for-subscription__text">Tellijale</span>', "")  # 2022.02.15
            curArtDesc = curArtDesc.replace('<span>Artikkel on kuulatav<br><a href="https://minumeedia.postimees.ee/kampaania/" target="_blank" class="my-media-link">digipaketi</a> tellijatele</span>', "")
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

            # image
            curArtImg = parsers_common.xpath_to("single", pageTree, '//meta[@property="og:image"]/@content', count=True)
            articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtImg)

            # pubDates magic from "24.12.2017 17:51" to datetime()
            curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
            curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dt%H:%M:%S%z")
            articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

            # sisu puudumise kontrollid
            if "kuulutused" in curArtUrl:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: kuulutused", 2)
            elif "karikatuur" in curArtUrl:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: karikatuur", 2)
            elif "galerii" in curArtUrl:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: galerii", 2)
            elif "pildid" in curArtUrl:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: pildid", 2)
            elif "pilt-" in curArtUrl:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: pilt", 2)
            elif "sundmused" in curArtUrl:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: sundmused", 2)
            else:
                if not curArtDesc1:
                    rss_print.print_debug(__file__, "tühi 1. plokk: (bold sissejuhatus) - " + curArtUrl, 0)
                if not curArtDesc2:
                    if not curArtDesc1 or not curArtDesc3:
                        rss_print.print_debug(__file__, "tühi 2. plokk: (tavatekst) - " + curArtUrl, 0)
                    else:
                        rss_print.print_debug(__file__, "tühi 2. plokk: (tavatekst) - " + curArtUrl, 1)
                if not curArtDesc3:
                    if not curArtDesc2:
                        rss_print.print_debug(__file__, "tühi 3. plokk: (hall väljajuhatus, meedia) - " + curArtUrl, 0)
                    else:
                        rss_print.print_debug(__file__, "tühi 3. plokk: (hall väljajuhatus, meedia) - " + curArtUrl, 1)

            # sisu kokkulangevuse kontrollid
            if curArtDesc1 and curArtDesc1 == curArtDesc2:
                rss_print.print_debug(__file__, "1. ja 2. plokk langevad kokku - " + curArtUrl, 0)
                rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc1, 1)
                rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 1)
            if curArtDesc2 and curArtDesc2 == curArtDesc3:
                rss_print.print_debug(__file__, "2. ja 3. plokk langevad kokku - " + curArtUrl, 0)
                rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 1)
                rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 1)
            if curArtDesc3 and curArtDesc3 == curArtDesc1:
                rss_print.print_debug(__file__, "3. ja 1. plokk langevad kokku - " + curArtUrl, 0)
                rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 1)
                rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc1, 1)

    return articleDataDict
