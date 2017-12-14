#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS faili kirjutamine
"""

from lxml import etree
import datetime
import time
from email import utils


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
    lastBuildDate.text = str(utils.formatdate(datetime.datetime.timestamp(datetime.datetime.now()), True, True))

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
            curArticlePubdate_datetime = list(dataset['articlePubDate'])[i[0]]
            curArticlePubdate_tuple = curArticlePubdate_datetime.timetuple()
            curArticlePubdate_timestamp = time.mktime(curArticlePubdate_tuple)
            curArticlePubdate_RFC2822 = utils.formatdate(curArticlePubdate_timestamp, True, True)

            item_pubDate = etree.SubElement(item, "pubDate")
            item_pubDate.text = curArticlePubdate_RFC2822

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
