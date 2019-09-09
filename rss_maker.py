#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS faili genereerimine ja kirjutamine
"""

import re
import time
from lxml import etree

import rss_print
import parsers_common


def rssmaker(dataset, titleText, domainText, linkText, descriptionText, hrefFullText):
    root = etree.Element("rss", version="2.0")

    channel = etree.SubElement(root, "channel")

    title = etree.SubElement(channel, "title")
    title.text = titleText

    link = etree.SubElement(channel, "link")
    link.text = linkText

    description = etree.SubElement(channel, "description")
    description.text = descriptionText

    # https://cyber.harvard.edu/rss/rss.html:
    # "Sat, 07 Sep 2002 09:42:31 GMT" ehk https://tools.ietf.org/html/rfc822
    curTimeFormat = "%a, %d %b %Y %H:%M:%S %z"  # Fri, 17 May 2019 13:37:00 +0300
    curTimeFloat = time.time()
    curGenerTime = parsers_common.float_to_datetime(curTimeFloat, curTimeFormat)

    lastBuildDate = etree.SubElement(channel, "lastBuildDate")
    lastBuildDate.text = curGenerTime

    # https://cyber.harvard.edu/rss/rss.html#ltttlgtSubelementOfLtchannelgt:
    # "Number of minutes that indicates how long a channel can be cached before refreshing from the source."
    ttl = etree.SubElement(channel, "ttl")
    ttl.text = str(60)

    for i in range(0, len(dataset["urls"])):
        item = etree.SubElement(channel, "item")

        if ("urls" in dataset and i < len(list(dataset["urls"])) and list(dataset["urls"])[i] is not None):
            itemGuid = etree.SubElement(item, "guid")  # https://cyber.harvard.edu/rss/rss.html: A string that uniquely identifies the item.
            itemLink = etree.SubElement(item, "link")

            curValue = list(dataset["urls"])[i]
            curValue = curValue.rstrip("/")

            if (curValue.find('http', 0, 4) == -1):
                rss_print.print_debug(__file__, "lingist ei leitud http-d: " + str(curValue), 3)
                curValue = parsers_common.domain_url(domainText, curValue)

            curValueWithoutHttp = curValue
            curValueWithoutHttp = parsers_common.lstrip_string(curValueWithoutHttp, "https://")
            curValueWithoutHttp = parsers_common.lstrip_string(curValueWithoutHttp, "http://")
            curValueWithoutHttp = parsers_common.lstrip_string(curValueWithoutHttp, "www.")

            itemGuid.text = curValueWithoutHttp
            itemLink.text = curValue

        if ("titles" in dataset and i < len(list(dataset["titles"])) and list(dataset["titles"])[i] is not None):
            itemTitle = etree.SubElement(item, "title")

            curValue = list(dataset["titles"])[i]
            curValue = curValue.replace("<br>", " ")
            curValue = curValue.strip()
            curValue = parsers_common.capitalize_first(curValue)
            itemTitle.text = curValue
        else:
            rss_print.print_debug(__file__, "järgneval aadressil puudus vajalik pealkiri: " + str(itemLink.text))
            itemTitle = etree.SubElement(item, "title")
            itemTitle.text = title.text + " " + itemGuid.text

        if ("descriptions" in dataset and i < len(list(dataset["descriptions"])) and list(dataset["descriptions"])[i] is not None):
            itemDescription = etree.SubElement(item, "description")

            curValue = list(dataset["descriptions"])[i]

            # remove trackers from links
            curValue = re.sub(r'" onclick[\s\S]*?;', "", curValue)
            curValue = re.sub(r'_ga=[0-9.-]*', "", curValue)
            curValue = re.sub(r'fbclid=[0-9A-Za-z-]*', "", curValue)
            curValue = re.sub(r'gclid=[0-9A-Za-z-_]*', "", curValue)
            curValue = re.sub(r'utm_source=pm_fb[0-9A-Za-z&_=]*', "", curValue)
            curValue = re.sub(r'&_[a-zA-Z0-9_-]*', "", curValue)  # delfi

            curValue = curValue.replace("?&", "?")

            # fix links addresses
            curValue = curValue.replace('src="./', 'src="' + domainText + '/')
            curValue = curValue.replace('src="/', 'src="' + domainText + '/')
            curValue = curValue.replace('href="./', 'href="' + domainText + '/')
            curValue = curValue.replace('href="/', 'href="' + domainText + '/')

            # remove useless space
            curValue = curValue.replace("<br/>", "<br>")
            curValue = curValue.replace("<br><br>", "<br>")
            curValue = curValue.strip()
            curValue = parsers_common.lstrip_string(curValue, "<br>")

            curValue = parsers_common.capitalize_first(curValue)
            itemDescription.text = curValue.encode('ascii', 'xmlcharrefreplace').strip()
        else:
            rss_print.print_debug(__file__, "järgneval pealkirjal puudus vajalik kirjeldus: " + str(itemTitle.text))
            itemDescription = etree.SubElement(item, "description")
            itemDescription.text = itemTitle.text

        if ("pubDates" in dataset and i < len(list(dataset["pubDates"])) and list(dataset["pubDates"])[i] is not None):
            itemPubdate = etree.SubElement(item, "pubDate")  # https://cyber.harvard.edu/rss/rss.html

            curValue = list(dataset["pubDates"])[i]

            curTimeFloat = time.time()

            postTimeFloat = parsers_common.raw_to_float(curValue, curTimeFormat)
            postTimeFloatLimit = (curTimeFloat - 31 * 24 * 60 * 60)

            if postTimeFloat <= 1:
                rss_print.print_debug(__file__, "posti: '" + itemTitle.text + "' aeg: '" + str(curValue) + "' on eelajalooline!, asendame hetkeajaga", 0)
                curValue = parsers_common.float_to_datetime(curTimeFloat, curTimeFormat)
                itemPubdate.text = curValue
            elif postTimeFloat < postTimeFloatLimit:
                rss_print.print_debug(__file__, "posti: '" + itemTitle.text + "' aeg: '" + str(curValue) + "' on vanem kui 31 päeva, eemaldame kande", 2)
                channel.remove(item)
            elif postTimeFloat > curTimeFloat:
                rss_print.print_debug(__file__, "posti: '" + itemTitle.text + "' aeg: '" + str(curValue) + "' on tulevikust?", 0)
                itemPubdate.text = curValue
            else:
                itemPubdate.text = curValue

        if ("images" in dataset and i < len(list(dataset["images"])) and list(dataset["images"])[i] is not None):
            # https://cyber.harvard.edu/rss/rss.html
            # <enclosure url="http://www.scripting.com/mp3s/weatherReportSuite.mp3" length="12216320" type="audio/mpeg" />

            curValue = list(dataset["images"])[i]
            encType = ""

            if curValue.find("url(") > 0:
                rss_print.print_debug(__file__, "korrastame parsimata meedialingi:': " + str(curValue), 1)
                curValue = curValue.split("url('")[-1].strip("');")
                encType = "image/jpeg"

            if curValue.find("//") == 0:
                rss_print.print_debug(__file__, "lisame meedialingi algusesse 'http:': " + str(curValue), 2)
                curValue = "http:" + curValue

            curValue = curValue.replace("https", "http")

            if len(curValue) < len(domainText + "1.jpg"):
                rss_print.print_debug(__file__, "ei lisa RSS-i meedialinki, kuna see on liiga lühike: '" + str(curValue) + "'", 0)
            else:
                if (curValue.find('http', 0, 4) == -1):
                    rss_print.print_debug(__file__, "meedialingist ei leitud http-d: '" + str(curValue) + "'", 3)
                    curValue = parsers_common.domain_url(domainText, curValue)

                if (encType == ""):
                    if ".jpg" in (curValue):
                        encType = "image/jpeg"
                    elif ".jpeg" in (curValue):
                        encType = "image/jpeg"
                    elif ".png" in (curValue):
                        encType = "image/png"
                    elif ".mp3" in (curValue):
                        encType = "audio/mpeg"

                etree.SubElement(item, "enclosure", {'url': curValue, 'length': '', 'type': encType, })

        if ("authors" in dataset and i < len(list(dataset["authors"])) and list(dataset["authors"])[i] is not None):
            itemAuthor = etree.SubElement(item, "author")
            itemAuthorName = etree.SubElement(itemAuthor, "name")

            curValue = list(dataset["authors"])[i]
            itemAuthorName.text = curValue

    return(etree.ElementTree(root))
