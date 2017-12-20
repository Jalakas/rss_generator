#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS faili genereerimine ja kirjutamine
"""

import datetime
import time
from email import utils
from lxml import etree


def rssmaker(dataset, title_text, link_text, description_text):
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
    ttl.text = str(120)

    for i in range(0, len(dataset['articleIds'])):
        item = etree.SubElement(channel, "item")

        item_title = etree.SubElement(item, "title")
        item_title.text = list(dataset['articleTitles'])[i].encode('ascii', 'xmlcharrefreplace')

        item_link = etree.SubElement(item, "link")
        item_link.text = list(dataset['articleUrls'])[i].encode('ascii', 'xmlcharrefreplace')

        if ('articleDescriptions' in dataset and i < len(list(dataset['articleDescriptions'])) and list(dataset['articleDescriptions'])[i] is not None):
            item_description = etree.SubElement(item, "description")
            item_description.text = list(dataset['articleDescriptions'])[i].encode('ascii', 'xmlcharrefreplace')
        else:
            print(("rssmaker: järgneval pealkirjal puudus vajalik kirjeldus: " + str(item_title.text)))
            item_description = etree.SubElement(item, "description")
            item_description.text = item_title.text

        if ('articlePubDates' in dataset and i < len(list(dataset['articlePubDates'])) and list(dataset['articlePubDates'])[i] is not None):
            # https://cyber.harvard.edu/rss/rss.html: Tue, 03 Jun 2003 09:39:21 GMT
            item_pubDate = etree.SubElement(item, "pubDate")

            art_PubDate_datetime = list(dataset['articlePubDates'])[i]
            art_PubDate_tuple = art_PubDate_datetime.timetuple()
            art_PubDate_timestamp = time.mktime(art_PubDate_tuple)
            art_PubDate_RFC2822 = utils.formatdate(art_PubDate_timestamp, True, True)
            item_pubDate.text = art_PubDate_RFC2822

        if ('articleIds' in dataset and i < len(list(dataset['articleIds'])) and list(dataset['articleIds'])[i] is not None):
            # https://cyber.harvard.edu/rss/rss.html: A string that uniquely identifies the item.
            item_guid = etree.SubElement(item, "guid")
            item_guid.text = list(dataset['articleIds'])[i].encode('ascii', 'xmlcharrefreplace')

        if ('articleImages' in dataset and i < len(list(dataset['articleImages'])) and list(dataset['articleImages'])[i] is not None):
            # https://cyber.harvard.edu/rss/rss.html
            # <enclosure url="http://www.scripting.com/mp3s/weatherReportSuite.mp3" length="12216320" type="audio/mpeg" />
            curImgLink = list(dataset['articleImages'])[i]
            if len(curImgLink) < len(link_text + "1.jpg"):
                print(("rssmaker: ei lisa rssi pildilinki, kuna see on liiga lühike: " + str(curImgLink)))
            else:
                item_enc_url = str(curImgLink).encode('ascii', 'xmlcharrefreplace')
                if b'.jpg' in (item_enc_url):
                    item_enc_type = "image/jpeg"
                elif b'.png' in (item_enc_url):
                    item_enc_type = "image/png"
                else:
                    item_enc_type = ""

                enclosure_attrib = {'url': item_enc_url,
                                    'length': '',
                                    'type': item_enc_type,
                                   }

                etree.SubElement(item, "enclosure", enclosure_attrib)

    return(etree.ElementTree(root))
