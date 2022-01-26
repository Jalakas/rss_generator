
import parsers_common
import parsers_datetime


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["images"] =     parsers_common.xpath_to("list", pageTree, '//div[@class="td-image-container"]/div[@class="td-module-thumb"]/a/span/@style')
    articleDataDict["pubDates"] =   parsers_common.xpath_to("list", pageTree, '//div[@class="td-module-meta-info"]/div[@class="td-editor-date"]/span/span/time/@datetime')
    articleDataDict["titles"] =     parsers_common.xpath_to("list", pageTree, '//div[@class="td-module-meta-info"]/h3[@class="entry-title td-module-title"]/a/text()')
    articleDataDict["urls"] =       parsers_common.xpath_to("list", pageTree, '//div[@class="td-module-meta-info"]/h3[@class="entry-title td-module-title"]/a/@href')

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # pubDates magic from "2020-02-14T17:22:25+00:00" to datetime()
        curArtPubDate = parsers_common.get(articleDataDict["pubDates"], i)
        curArtPubDate = parsers_datetime.raw_to_datetime(curArtPubDate, "%Y-%m-%dT%H:%M:%S%z")
        articleDataDict["pubDates"] = parsers_common.list_add_or_assign(articleDataDict["pubDates"], i, curArtPubDate)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # author
            curArtAuthor = parsers_common.xpath_to("single", pageTree, '//h3[@class="author vcard"]/span[@class="fn"]/a/text()', multi=True)
            articleDataDict["authors"] = parsers_common.list_add_or_assign(articleDataDict["authors"], i, curArtAuthor)

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="td-post-content tagdiv-type"]', parent=True)
            curArtDesc = curArtDesc.split("</figure>")[-1]
            # asendame jama
            curArtDesc = curArtDesc.replace('<h2 style="text-align: center">Artikli lugemiseks tellige digipakett või <strong><a href="https://online.le.ee/tellimine/">logige</a></strong> sisse!</h2>', "")
            curArtDesc = curArtDesc.replace('<h3 id="wc-comment-header">Kommenteeri</h3>', "")
            curArtDesc = curArtDesc.replace('<h5 id="reegel">NB! Kommentaarid on avaldatud lugejate poolt. Kommentaare ei toimetata. Nende sisu ei pruugi ühtida toimetuse seisukohtadega. Kui märkad sobimatut postitust, teavita sellest moderaatoreid, vajutades lipukese ikooni.</h5>', "")
            curArtDesc = curArtDesc.replace('<img class="aligncenter size-full wp-image-352428" src="https://online.le.ee/wp-content/uploads/2022/01/tasuline.png" alt="" width="688" height="101">', "")
            curArtDesc = curArtDesc.replace('<span>Teata ebasobivast kommentaarist</span>', "")

            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
