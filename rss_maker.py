#!/usr/bin/env python3

"""
    RSS failisisu genereerimine
"""

from lxml import etree

import parsers_common
import parsers_datetime
import rss_print


def rssmaker(dataset, titleText, domainText, linkText, descriptionText):
    rss_print.print_debug(__file__, "asume koostame rss-i: " + linkText, 3)

    root = etree.Element("rss", version="2.0")

    channel = etree.SubElement(root, "channel")

    title = etree.SubElement(channel, "title")
    title.text = titleText

    link = etree.SubElement(channel, "link")
    link.text = linkText

    description = etree.SubElement(channel, "description")
    description.text = descriptionText

    # https://cyber.harvard.edu/rss/rss.html: "Sat, 07 Sep 2002 09:42:31 GMT" ehk https://tools.ietf.org/html/rfc822
    curTimeFormat = "%a, %d %b %Y %H:%M:%S %z"  # Fri, 17 May 2019 13:37:00 +0300
    curTimeFloat = parsers_datetime.time_float()
    curGenerTime = parsers_datetime.float_to_datetime(curTimeFloat, curTimeFormat)

    lastBuildDate = etree.SubElement(channel, "lastBuildDate")
    lastBuildDate.text = curGenerTime

    # https://cyber.harvard.edu/rss/rss.html#ltttlgtSubelementOfLtchannelgt:
    # "Number of minutes that indicates how long a channel can be cached before refreshing from the source."
    ttl = etree.SubElement(channel, "ttl")
    ttl.text = str(60)

    for i in range(len(dataset["urls"])):
        item = etree.SubElement(channel, "item")

        if ("urls" in dataset and i < len(list(dataset["urls"])) and list(dataset["urls"])[i] is not None):
            itemGuid = etree.SubElement(item, "guid")  # https://cyber.harvard.edu/rss/rss.html: A string that uniquely identifies the item.
            itemLink = etree.SubElement(item, "link")

            curValue = list(dataset["urls"])[i]
            curValue = curValue.rstrip("/")
            if curValue.find('http', 0, 4) != 0:
                rss_print.print_debug(__file__, "lingist ei leitud http-d: " + curValue, 3)
                curValue = parsers_common.domain_url(domainText, curValue)

            curValueWithoutHttp = parsers_common.simplify_link(curValue)

            itemGuid.text = curValueWithoutHttp
            itemLink.text = curValue

        if ("titles" in dataset and i < len(list(dataset["titles"])) and list(dataset["titles"])[i] is not None):
            itemTitle = etree.SubElement(item, "title")

            curValue = list(dataset["titles"])[i]
            curValue = curValue.replace("<br>", " ")
            curValue = curValue.replace("  ", " ")
            curValue = curValue.strip()
            curValue = parsers_common.capitalize_first(curValue)
            itemTitle.text = curValue.encode('ascii', 'xmlcharrefreplace')
        else:
            rss_print.print_debug(__file__, "järgneval aadressil puudus vajalik pealkiri: " + str(itemLink.text), 0)
            itemTitle = etree.SubElement(item, "title")
            itemTitle.text = title.text + " " + itemGuid.text

        if ("descriptions" in dataset and i < len(list(dataset["descriptions"])) and list(dataset["descriptions"])[i] is not None):
            itemDescription = etree.SubElement(item, "description")

            curValue = list(dataset["descriptions"])[i]
            curValue = curValue.strip()
            curValue = parsers_common.lchop(curValue, "<br>")
            curValue = parsers_common.html_post_cleanup(curValue)
            curValue = parsers_common.capitalize_first(curValue)

            # konverdime sisu ascii-sse
            itemDescription.text = curValue.encode('ascii', 'xmlcharrefreplace')
        else:
            rss_print.print_debug(__file__, "järgneval pealkirjal puudus vajalik kirjeldus: " + str(itemTitle.text), 0)
            itemDescription = etree.SubElement(item, "description")
            itemDescription.text = itemTitle.text

        if ("pubDates" in dataset and i < len(list(dataset["pubDates"])) and list(dataset["pubDates"])[i] is not None):
            itemPubdate = etree.SubElement(item, "pubDate")  # https://cyber.harvard.edu/rss/rss.html

            curValue = list(dataset["pubDates"])[i]

            curTimeFloat = parsers_datetime.time_float()

            postTimeFloat = parsers_datetime.raw_to_float(curValue, curTimeFormat)
            postTimeFloatLimit = (curTimeFloat - 31 * 24 * 60 * 60)

            if postTimeFloat <= 1:
                rss_print.print_debug(__file__, "posti: '" + itemTitle.text + "' aeg: '" + curValue + "' on eelajalooline!, asendame hetkeajaga", 0)
                curValue = parsers_datetime.float_to_datetime(curTimeFloat, curTimeFormat)
                itemPubdate.text = curValue
            elif postTimeFloat < postTimeFloatLimit:
                rss_print.print_debug(__file__, "posti: '" + itemTitle.text + "' aeg: '" + curValue + "' on vanem kui 31 päeva, eemaldame kande", 2)
                channel.remove(item)
            elif postTimeFloat > curTimeFloat:
                rss_print.print_debug(__file__, "posti: '" + itemTitle.text + "' aeg: '" + curValue + "' on tulevikust?", 0)
                itemPubdate.text = curValue
            else:
                itemPubdate.text = curValue

        if ("images" in dataset and i < len(list(dataset["images"])) and list(dataset["images"])[i] is not None):
            # https://cyber.harvard.edu/rss/rss.html
            # <enclosure url="http://www.scripting.com/mp3s/weatherReportSuite.mp3" length="12216320" type="audio/mpeg" />

            curValue = list(dataset["images"])[i]
            encType = ""

            if curValue.find("url(") > 0:
                rss_print.print_debug(__file__, "korrastame parsimata meedialingi:': " + curValue, 1)
                curValue = curValue.split("url('")[-1].strip("');")
                encType = "image/jpeg"

            if curValue.startswith("//"):
                rss_print.print_debug(__file__, "lisame meedialingi algusesse 'http:': " + curValue, 2)
                curValue = "http:" + curValue

            curValue = curValue.replace("https", "http")

            if len(curValue) < len(domainText + "1.jpg"):
                rss_print.print_debug(__file__, "ei lisa RSS-i meedialinki, kuna see on liiga lühike: '" + curValue + "'", 0)
            else:
                if curValue.find('http', 0, 4) < 0:
                    rss_print.print_debug(__file__, "meedialingi algusest ei leitud 'http'-d: '" + curValue + "'", 1)
                    curValue = parsers_common.domain_url(domainText, curValue)

                if curValue.rfind('http') > 0:
                    rss_print.print_debug(__file__, "meedialingi keskelt leiti 'http': '" + curValue + "'", 0)

                if encType == "":
                    if ".jpg" in curValue:
                        encType = "image/jpeg"
                    elif ".jpeg" in curValue:
                        encType = "image/jpeg"
                    elif ".png" in curValue:
                        encType = "image/png"
                    elif ".mp3" in curValue:
                        encType = "audio/mpeg"

                etree.SubElement(item, "enclosure", {'url': curValue, 'type': encType, })

        if ("authors" in dataset and i < len(list(dataset["authors"])) and list(dataset["authors"])[i] is not None):
            itemAuthor = etree.SubElement(item, "author")
            itemAuthorName = etree.SubElement(itemAuthor, "name")

            curValue = list(dataset["authors"])[i]
            itemAuthorName.text = curValue.encode('ascii', 'xmlcharrefreplace')

    ret = etree.ElementTree(root)

    return ret
