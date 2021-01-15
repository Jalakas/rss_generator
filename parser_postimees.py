#!/usr/bin/env python3

import parsers_datetime
import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    articleDataDict["pubDates"] = parsers_common.xpath_to_list(pageTree, '//div[@class="article-content"]/div[@class="article-content__meta"]/span[@class="article-content__date-published"]/text()')
    articleDataDict["pubDatesDay"] = parsers_common.xpath_to_list(pageTree, '//div[@class="article-content"]/div[@class="article-content__meta"]/span[@class="article-content__date-published"]/span/text()')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="article-content"]/a[@class="article-content__headline"]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="article-content"]/a[@class="article-content__headline"]/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # timeformat magic from "24.12.2017 17:51" to datetime()

        curArtPubDateDay = ""
        if len(articleDataDict["pubDatesDay"]) - 1 >= i:
            curArtPubDateDay = articleDataDict["pubDatesDay"][i]
            curArtPubDateDay = parsers_datetime.replace_string_with_timeformat(curArtPubDateDay, "Eile", "%d.%m.%Y", offSetDays=-1)
            curArtPubDateDay = parsers_datetime.replace_string_with_timeformat(curArtPubDateDay, "Täna", "%d.%m.%Y", offSetDays=0)

        curArtPubDate = articleDataDict["pubDates"][i]
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDateDay + curArtPubDate, "%d.%m.%Y, %H:%M")
        articleDataDict["pubDates"][i] = curArtPubDate

        if (rss_config.GET_ARTICLE_BODIES is True and i < rss_config.MAX_ARTICLE_BODIES):
            # load article into tree
            pageTree = parsers_common.get_article_tree(session, domain, articleDataDict["urls"][i], noCache=False)

            # author
            curArtAuthor = parsers_common.xpath_to_single(pageTree, '//span[@class="article-authors__name"]/text()', multi=True)
            articleDataDict["authors"].append(curArtAuthor)

            # description1 - enne pilti
            curArtDesc1 = ""
            if curArtDesc1 == "":
                curArtDesc1 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--articleBullets"]', parent=True, count=True)
            if curArtDesc1 == "":
                curArtDesc1 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--video"]', parent=True, count=True)

            # description2 - pildi ja kuulamise vahel
            curArtDesc2 = ""
            if curArtDesc2 == "":
                curArtDesc2 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body__item--lead"]', parent=True, count=True, multi=True)
            if curArtDesc2 == "":
                curArtDesc2 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body--first-child article-body__item--lead"]', parent=True, count=True)

            # description3 - pärast kuulamist
            curArtDesc3 = ""
            if curArtDesc3 == "":
                if "produtsent-merle-kollom-liiguvad-suurte-lavade-poole" in articleDataDict["urls"][i]:
                    parsers_common.xpath_debug(pageTree)
                curArtDesc3 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--htmlElement"]', parent=True, count=True, multi=True)

            # description4 - hall väljajuhatus
            curArtDesc4 = ""
            if curArtDesc4 == "":
                curArtDesc4 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--htmlElement article-body--teaser"]', parent=True, count=True)
            if curArtDesc4 == "":
                curArtDesc4 = parsers_common.xpath_to_single(pageTree, '//div[@class="article-body__item article-body__item--gallery"]', parent=True, count=True, multi=True)

            # image
            curArtImg = ""
            if curArtImg == "":
                curArtImg = parsers_common.xpath_to_single(pageTree, '//figure[1]/img[1]/@src', count=True)
            if curArtImg == "":
                curArtImg = parsers_common.xpath_to_single(pageTree, '//div[@class="article-superheader article-superheader--figure"]/div[@class="article-superheader__background"]/@style', count=True)
                curArtImg = curArtImg.split("url('")[-1].strip("');")
            if curArtImg == "":
                curArtImg = parsers_common.xpath_to_single(pageTree, '//meta[@property="og:image"]/@content', count=True)

            # kontrollid
            if "-kuulutused-" in articleDataDict["urls"][i]:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: kuulutused", 2)
            elif "-karikatuur" in articleDataDict["urls"][i]:
                rss_print.print_debug(__file__, "ei kontrolli plokke, kuna: karikatuur", 2)
            else:
                if curArtDesc1 == "":
                    rss_print.print_debug(__file__, "1. kirjeldusplokk on tühi. (Pildieelne loendiplokk puudub?)", 2)
                else:
                    rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc1, 4)
                if curArtDesc2 == "":
                    rss_print.print_debug(__file__, "2. kirjeldusplokk on tühi. (Pildi järel, enne kuulamist plokk puudub?)", 0)
                else:
                    rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 4)
                if curArtDesc3 == "":
                    rss_print.print_debug(__file__, "3. kirjeldusplokk on tühi. (Pärast kuulamist plokk puudub?)", 0)
                else:
                    rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 4)
                if curArtDesc4 == "":
                    rss_print.print_debug(__file__, "4. kirjeldusplokk on tühi. (Hall fadeout plokk puudub?)", 2)
                else:
                    rss_print.print_debug(__file__, "curArtDesc4 = " + curArtDesc4, 4)
                if curArtImg == "":
                    rss_print.print_debug(__file__, "pilti ei leitud.", 0)
                else:
                    rss_print.print_debug(__file__, "curArtImg = " + curArtImg, 4)
                if curArtDesc1 != "" and curArtDesc1 == curArtDesc2:
                    rss_print.print_debug(__file__, "1. ja 2. kirjeldusplokk langevad kokku", 0)
                    rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc1, 1)
                    rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 1)
                if curArtDesc2 != "" and curArtDesc2 == curArtDesc3:
                    rss_print.print_debug(__file__, "2. ja 3. kirjeldusplokk langevad kokku", 0)
                    rss_print.print_debug(__file__, "curArtDesc2 = " + curArtDesc2, 1)
                    rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 1)
                if curArtDesc3 != "" and curArtDesc3 == curArtDesc4:
                    rss_print.print_debug(__file__, "3. ja 4. kirjeldusplokk langevad kokku", 0)
                    rss_print.print_debug(__file__, "curArtDesc3 = " + curArtDesc3, 1)
                    rss_print.print_debug(__file__, "curArtDesc4 = " + curArtDesc4, 1)
                if curArtDesc4 != "" and curArtDesc4 == curArtDesc1:
                    rss_print.print_debug(__file__, "4. ja 1. kirjeldusplokk langevad kokku", 0)
                    rss_print.print_debug(__file__, "curArtDesc4 = " + curArtDesc3, 1)
                    rss_print.print_debug(__file__, "curArtDesc1 = " + curArtDesc4, 1)

            curArtDesc = curArtDesc1 + ' ' + curArtDesc2 + ' ' + curArtDesc3 + ' ' + curArtDesc4
            curArtDesc = curArtDesc.replace('<span class="button--for-subscription"><span>Tellijale</span></span>', "")
            articleDataDict["descriptions"].append(curArtDesc)

            articleDataDict["images"].append(curArtImg)

    return articleDataDict
