#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS faili kirjutamine
"""

from lxml import etree
import datetime


def rssmaker(dataset, title_text, link_text, description_text):
    version = "2.0"
    root = etree.Element("rss", version=version)

    channel = etree.SubElement(root, "channel")

    title = etree.SubElement(channel, "title")
    title.text = title_text
    link = etree.SubElement(channel, "link")
    link.text = link_text
    description = etree.SubElement(channel, "description")
    description.text = description_text

    # https://cyber.harvard.edu/rss/rss.html: Sat, 07 Sep 2002 09:42:31 GMT
    lastBuildDate = etree.SubElement(channel, "lastBuildDate")
    lastBuildDate.text = str(datetime.datetime.utcnow())

    for i in enumerate(dataset['articleIds']):
        item = etree.SubElement(channel, "item")

        item_title = etree.SubElement(item, "title")
        item_title.text = list(dataset['articleTitles'])[i[0]].encode('ascii', 'xmlcharrefreplace')

        item_link = etree.SubElement(item, "link")
        item_link.text = list(dataset['articleUrls'])[i[0]].encode('ascii', 'xmlcharrefreplace')

        item_description = etree.SubElement(item, "description")
        item_description.text = list(dataset['articleHeaders'])[i[0]].encode('ascii', 'xmlcharrefreplace')

        if 'articlePubDate' in dataset:
            # https://cyber.harvard.edu/rss/rss.html: Tue, 03 Jun 2003 09:39:21 GMT
            item_pubDate = etree.SubElement(item, "pubDate")
            item_pubDate.text = list(dataset['articlePubDate'])[i[0]].encode('ascii', 'xmlcharrefreplace')

        if 'articleIds' in dataset:
            # https://cyber.harvard.edu/rss/rss.html: A string that uniquely identifies the item.
            item_guid = etree.SubElement(item, "guid")
            item_guid.text = list(dataset['articleIds'])[i[0]].encode('ascii', 'xmlcharrefreplace')

        if 'articleImages' in dataset:
            # https://cyber.harvard.edu/rss/rss.html:
            # <enclosure url="http://www.scripting.com/mp3s/weatherReportSuite.mp3" length="12216320" type="audio/mpeg" />
            curImgLink = list(dataset['articleImages'])[i[0]]
            if len(curImgLink) < len(link_text + "1.jpg"):
                print("rssmaker: ei lisa rssi pildilinki, kuna see on liiga lühike: " + str(curImgLink))
            else:
                item_enclosure = etree.SubElement(item, "enclosure")
                item_enclosure_url = etree.SubElement(item_enclosure, "url")
                item_enclosure_url.text = str(curImgLink).encode('ascii', 'xmlcharrefreplace')
                item_enclosure_len = etree.SubElement(item_enclosure, "length")
                item_enclosure_len.text = ''  # https://jarvateataja.postimees.ee/rss puhul toimis
                item_enclosure_type = etree.SubElement(item_enclosure, "type")
                if '.jpg' in (item_enclosure_url.text):
                    item_enclosure_type.text = "image/jpeg"

                elif '.png' in (item_enclosure_url.text):
                    item_enclosure_type.text = "image/png"
                else:
                    item_enclosure_type.text = ""

    return(etree.ElementTree(root))
