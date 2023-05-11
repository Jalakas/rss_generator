
"""
    RSS failisisu genereerimine.
"""

from lxml import etree

import parsers_common
import parsers_datetime
import rss_config
import rss_print


def rssmaker(dataset, titleText, domainText, linkText, descriptionText):
    root = etree.Element("rss", version="2.0")

    channel = etree.SubElement(root, "channel")

    title = etree.SubElement(channel, "title")
    title.text = titleText

    link = etree.SubElement(channel, "link")
    link.text = linkText

    description = etree.SubElement(channel, "description")
    description.text = descriptionText

    # https://cyber.harvard.edu/rss/rss.html: "Sat, 07 Sep 2002 09:42:31 GMT" ehk https://tools.ietf.org/html/rfc822
    curTimeFloat = parsers_datetime.time_float()
    curTimeFloatLimit = curTimeFloat - (31 * 24 * 60 * 60)
    curTimeFormat = "%a, %d %b %Y %H:%M:%S %z"  # Fri, 17 May 2019 13:37:00 +0300
    curGenerTime = parsers_datetime.float_to_datetime_rfc2822(curTimeFloat)

    lastBuildDate = etree.SubElement(channel, "lastBuildDate")
    lastBuildDate.text = curGenerTime

    # https://cyber.harvard.edu/rss/rss.html#ltttlgtSubelementOfLtchannelgt:
    # "Number of minutes that indicates how long a channel can be cached before refreshing from the source."
    ttl = etree.SubElement(channel, "ttl")
    ttl.text = str(12 * 60)

    urlsLen = len(dataset["urls"])
    urlsLenStr = str(urlsLen)
    for i in range(urlsLen):
        curKandeString = str(i + 1) + "/" + urlsLenStr

        if parsers_common.get(dataset["urls"], i, printWarning=0):
            item = etree.SubElement(channel, "item")
            itemLink = etree.SubElement(item, "link")

            curValue = dataset["urls"][i]
            curValue = curValue.rstrip("/")
            if not curValue.startswith("http"):
                rss_print.print_debug(__file__, "kande(" + curKandeString + ") lingi algusest ei leitud 'http': " + curValue, 3)
                curValue = parsers_common.str_domain_url(domainText, curValue)
            if "http://" in curValue and "https://" in domainText:
                rss_print.print_debug(__file__, "kande(" + curKandeString + ") lingist leiti 'http://': " + curValue, 1)
                curValue = curValue.replace("http://", "https://")
            itemLink.text = curValue

            # https://cyber.harvard.edu/rss/rss.html: A string that uniquely identifies the item.
            itemGuid = etree.SubElement(item, "guid")
            curValueWithoutHttp = parsers_common.str_lchop_url(curValue)
            itemGuid.text = curValueWithoutHttp.encode('ascii', 'xmlcharrefreplace')
        else:
            rss_print.print_debug(__file__, "kande(" + curKandeString + ") puudub vajalik url, katkestame", 0)
            continue

        if parsers_common.get(dataset["titles"], i, printWarning=0):
            itemTitle = etree.SubElement(item, "title")
            curValue = dataset["titles"][i]
            curValue = curValue.replace("<br>", " ")
            curValue = parsers_common.str_cleanup_title(curValue)
            itemTitle.text = curValue.encode('ascii', 'xmlcharrefreplace')
        else:
            rss_print.print_debug(__file__, "kande(" + curKandeString + ") aadressil puudub vajalik pealkiri: " + str(itemLink.text), 0)
            itemTitle = etree.SubElement(item, "title")
            itemTitle.text = title.text + " " + itemGuid.text

        if parsers_common.get(dataset["descriptions"], i, printWarning=0):
            itemDescription = etree.SubElement(item, "description")
            curValue = dataset["descriptions"][i]
            curValue = parsers_common.str_cleanup_post(curValue)
            curValue = parsers_common.str_cleanup_description(curValue)
            itemDescription.text = curValue.encode('ascii', 'xmlcharrefreplace')
        else:
            rss_print.print_debug(__file__, "kande(" + curKandeString + ") pealkirjal puudub vajalik kirjeldus: '" + str(itemTitle.text) + "' - " + str(itemLink.text), 0)
            itemDescription = etree.SubElement(item, "description")
            itemDescription.text = itemTitle.text

        if parsers_common.get(dataset["pubDates"], i, printWarning=0):
            curValue = dataset["pubDates"][i]
            postTimeFloat = parsers_datetime.raw_to_float(curValue, curTimeFormat)

            if rss_config.UPLOAD_TIME_LIMIT is True and postTimeFloat < curTimeFloatLimit:
                rss_print.print_debug(__file__, "kande(" + curKandeString + ") '" + itemTitle.text + "' aeg: '" + curValue + "' on vanem kui 31 päeva, eemaldame kande", 2)
                channel.remove(item)

            if postTimeFloat < 1:
                rss_print.print_debug(__file__, "kande(" + curKandeString + ") '" + itemTitle.text + "' aeg: '" + curValue + "' on eelajalooline!, asendame hetkeajaga", 0)
                curValue = parsers_datetime.float_to_datetime_rfc2822(curTimeFloat)
            elif postTimeFloat > curTimeFloat:
                rss_print.print_debug(__file__, "kande(" + curKandeString + ") '" + itemTitle.text + "' aeg: '" + curValue + "' on tulevikust?", 1)
            elif i == urlsLen and parsers_datetime.raw_to_float(dataset["pubDates"][i], curTimeFormat) < parsers_datetime.raw_to_float(dataset["pubDates"][i-1], curTimeFormat):
                    rss_print.print_debug(__file__, "kande(" + curKandeString + ") '" + itemTitle.text + "' aeg: '" + curValue + "' on eelmisest väiksem", 0)

            itemPubdate = etree.SubElement(item, "pubDate")  # https://cyber.harvard.edu/rss/rss.html
            itemPubdate.text = curValue

        if parsers_common.get(dataset["images"], i, printWarning=0):
            # https://cyber.harvard.edu/rss/rss.html
            # <enclosure url="http://www.scripting.com/mp3s/weatherReportSuite.mp3" length="12216320" type="audio/mpeg" />

            curValue = dataset["images"][i]
            encType = ""

            curValue = curValue.strip()

            if curValue.find("url(") > 0:
                rss_print.print_debug(__file__, "kande(" + curKandeString + ") korrastame parsimata meedialingi:': " + curValue, 1)
                curValue = curValue.split("url('")[-1].strip("');")
                encType = "image/jpeg"

            if curValue.startswith("//"):
                rss_print.print_debug(__file__, "kande(" + curKandeString + ") lisame meedialingi algusesse 'http:': " + curValue, 2)
                curValue = "http:" + curValue

            curValue = curValue.replace("https", "http")

            if len(curValue) < len(domainText + "1.jpg"):
                rss_print.print_debug(__file__, "kande(" + curKandeString + ") ei lisa RSS-i meedialinki, kuna see on liiga lühike: '" + curValue + "'", 0)
            else:
                if not curValue.startswith("http"):
                    rss_print.print_debug(__file__, "kande(" + curKandeString + ") meedialingi algusest ei leitud 'http'-d: '" + curValue + "'", 1)
                    curValue = parsers_common.str_domain_url(domainText, curValue)

                if curValue.rfind('http') > 0:
                    rss_print.print_debug(__file__, "kande(" + curKandeString + ") meedialingi keskelt leiti 'http': '" + curValue + "'", 0)

                if not encType:
                    if (".jpg" in curValue) or (".jpeg" in curValue):
                        encType = "image/jpeg"
                    elif ".png" in curValue:
                        encType = "image/png"
                    elif ".mp3" in curValue:
                        encType = "audio/mpeg"

                curValue = curValue.replace("&", "%26")
                curValue = curValue.encode('ascii', 'xmlcharrefreplace')
                etree.SubElement(item, "enclosure", {'url': curValue, 'type': encType})

        if parsers_common.get(dataset["authors"], i, printWarning=0):
            curValue = dataset["authors"][i]
            if curValue.upper() != titleText.upper():
                itemAuthor = etree.SubElement(item, "author")
                itemAuthorName = etree.SubElement(itemAuthor, "name")
                itemAuthorName.text = curValue.encode('ascii', 'xmlcharrefreplace')

    ret = etree.ElementTree(root)

    return ret
