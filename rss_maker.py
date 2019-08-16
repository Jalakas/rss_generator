#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS faili genereerimine ja kirjutamine
"""

import datetime
import re
import time
from email import utils
from lxml import etree

import rss_print
import parsers_common


def rssmaker(dataset, title_text, domain_text, link_text, description_text, href_full_text):
    root = etree.Element("rss", version="2.0")

    channel = etree.SubElement(root, "channel")

    title = etree.SubElement(channel, "title")
    title.text = title_text

    link = etree.SubElement(channel, "link")
    link.text = link_text

    description = etree.SubElement(channel, "description")
    description.text = description_text

    # https://cyber.harvard.edu/rss/rss.html:
    # "Sat, 07 Sep 2002 09:42:31 GMT" ehk https://tools.ietf.org/html/rfc822
    lastBuildDate = etree.SubElement(channel, "lastBuildDate")
    lastBuildDate.text = str(utils.formatdate(datetime.datetime.timestamp(datetime.datetime.now()), True, True))

    # https://cyber.harvard.edu/rss/rss.html#ltttlgtSubelementOfLtchannelgt:
    # "Number of minutes that indicates how long a channel can be cached before refreshing from the source."
    ttl = etree.SubElement(channel, "ttl")
    ttl.text = str(60)

    # atom = etree.SubElement(channel, "atom:link")
    # atom.set("href", href_full_text)
    # atom.set("rel", "self")
    # atom.set("type", "application/rss+xml")

    if (len(dataset["urls"]) < 1):
        rss_print.print_debug(__file__, "ei leitud ühtegi url-i lingilt: " + str(link_text))

    for i in range(0, len(dataset["urls"])):
        item = etree.SubElement(channel, "item")

        if ("urls" in dataset and i < len(list(dataset["urls"])) and list(dataset["urls"])[i] is not None):
            item_guid = etree.SubElement(item, "guid")  # https://cyber.harvard.edu/rss/rss.html: A string that uniquely identifies the item.
            item_link = etree.SubElement(item, "link")

            cur_value = list(dataset["urls"])[i]
            cur_value = cur_value.strip().rstrip("/")

            if (cur_value.find('http', 0, 4) == -1):
                rss_print.print_debug(__file__, "lingist ei leitud http-d: " + str(cur_value), 3)
                cur_value = parsers_common.domainUrl(domain_text, cur_value)

            cur_value_without_http = cur_value
            cur_value_without_http = parsers_common.lstrip_string(cur_value_without_http, "https://")
            cur_value_without_http = parsers_common.lstrip_string(cur_value_without_http, "http://")
            cur_value_without_http = parsers_common.lstrip_string(cur_value_without_http, "www.")

            item_guid.text = cur_value_without_http
            item_link.text = cur_value

        if ("titles" in dataset and i < len(list(dataset["titles"])) and list(dataset["titles"])[i] is not None):
            item_title = etree.SubElement(item, "title")

            cur_value = list(dataset["titles"])[i]
            cur_value = cur_value.replace("<br>", " ")
            cur_value = cur_value.strip()
            cur_value = parsers_common.capitalizeFirst(cur_value)
            item_title.text = cur_value
        else:
            rss_print.print_debug(__file__, "järgneval aadressil puudus vajalik pealkiri: " + str(item_link.text))
            item_title = etree.SubElement(item, "title")
            item_title.text = title.text + " " + item_guid.text

        if ("descriptions" in dataset and i < len(list(dataset["descriptions"])) and list(dataset["descriptions"])[i] is not None):
            item_description = etree.SubElement(item, "description")

            cur_value = list(dataset["descriptions"])[i]

            # remove trackers from links
            cur_value = re.sub(r'" onclick[\s\S]*?;', "", cur_value)
            cur_value = re.sub(r'_ga=[0-9.-]*', "", cur_value)
            cur_value = re.sub(r'fbclid=[0-9A-Za-z-]*', "", cur_value)
            cur_value = re.sub(r'gclid=[0-9A-Za-z-_]*', "", cur_value)
            cur_value = re.sub(r'utm_source=pm_fb[0-9A-Za-z&_=]*', "", cur_value)

            cur_value = cur_value.replace("?&", "?")

            # fix links addresses
            cur_value = cur_value.replace('src="./', 'src="' + domain_text + '/')
            cur_value = cur_value.replace('src="/', 'src="' + domain_text + '/')
            cur_value = cur_value.replace('href="./', 'href="' + domain_text + '/')
            cur_value = cur_value.replace('href="/', 'href="' + domain_text + '/')

            # remove useless space
            cur_value = cur_value.replace("<br/>", "<br>")
            cur_value = cur_value.replace("<br><br>", "<br>")
            cur_value = cur_value.strip()
            cur_value = parsers_common.lstrip_string(cur_value, "<br>")

            cur_value = parsers_common.capitalizeFirst(cur_value)
            item_description.text = cur_value.encode('ascii', 'xmlcharrefreplace').strip()
        else:
            rss_print.print_debug(__file__, "järgneval pealkirjal puudus vajalik kirjeldus: " + str(item_title.text))
            item_description = etree.SubElement(item, "description")
            item_description.text = item_title.text

        if ("pubDates" in dataset and i < len(list(dataset["pubDates"])) and list(dataset["pubDates"])[i] is not None):
            item_pubDate = etree.SubElement(item, "pubDate")  # https://cyber.harvard.edu/rss/rss.html

            cur_value = list(dataset["pubDates"])[i]

            curTimeFormat = "%a, %d %b %Y %H:%M:%S %z"  # Fri, 17 May 2019 13:37:00 +0300
            curTimeFloat = time.time()
            postTimeFloat = parsers_common.rawToFloat(cur_value, curTimeFormat)
            postTimeFloatLimit = (curTimeFloat - 31 * 24 * 60 * 60)
            if postTimeFloat <= 1:
                rss_print.print_debug(__file__, "posti: '" + item_title.text + "' aeg: '" + str(cur_value) + "' on eelajalooline!, asendame hetkeajaga", 0)
                cur_value = parsers_common.floatToDatetime(curTimeFloat, curTimeFormat)
                item_pubDate.text = cur_value.strip()
            elif postTimeFloat < postTimeFloatLimit:
                rss_print.print_debug(__file__, "posti: '" + item_title.text + "' aeg: '" + str(cur_value) + "' on vanem kui 31 päeva, eemaldame kande", 2)
                channel.remove(item)
            elif postTimeFloat > curTimeFloat:
                rss_print.print_debug(__file__, "posti: '" + item_title.text + "' aeg: '" + str(cur_value) + "' on tulevikust?", 0)
                item_pubDate.text = cur_value.strip()
            else:
                item_pubDate.text = cur_value.strip()

        if ("images" in dataset and i < len(list(dataset["images"])) and list(dataset["images"])[i] is not None):
            # https://cyber.harvard.edu/rss/rss.html
            # <enclosure url="http://www.scripting.com/mp3s/weatherReportSuite.mp3" length="12216320" type="audio/mpeg" />

            cur_value = list(dataset["images"])[i]

            if cur_value.find("//") == 0:
                rss_print.print_debug(__file__, "lisame meedialingi algusesse 'http:': " + str(cur_value), 1)
                cur_value = "http:" + cur_value

            cur_value = cur_value.replace("https", "http")

            if len(cur_value) < len(domain_text + "1.jpg"):
                rss_print.print_debug(__file__, "ei lisa RSS-i meedialinki, kuna see on liiga lühike: '" + str(cur_value) + "'", 0)
            else:
                if (cur_value.find('http', 0, 4) == -1):
                    rss_print.print_debug(__file__, "meedialingist ei leitud http-d: '" + str(cur_value) + "'", 3)
                    cur_value = parsers_common.domainUrl(domain_text, cur_value)
                item_enc_url = cur_value.strip()

                if ".jpg" in (item_enc_url):
                    item_enc_type = "image/jpeg"
                elif ".jpeg" in (item_enc_url):
                    item_enc_type = "image/jpeg"
                elif ".png" in (item_enc_url):
                    item_enc_type = "image/png"
                elif ".mp3" in (item_enc_url):
                    item_enc_type = "audio/mpeg"
                else:
                    item_enc_type = ""

                etree.SubElement(item, "enclosure", {'url': item_enc_url, 'length': '', 'type': item_enc_type, })

        if ("authors" in dataset and i < len(list(dataset["authors"])) and list(dataset["authors"])[i] is not None):
            item_author = etree.SubElement(item, "author")
            item_author_name = etree.SubElement(item_author, "name")

            cur_value = list(dataset["authors"])[i]
            item_author_name.text = cur_value.strip()

    return(etree.ElementTree(root))
