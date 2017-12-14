#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS faili kirjutamine
"""

from lxml import etree


def rssmaker(dataset, title_text, link_text, description_text):
    version = "2.0"
    root = etree.Element(
        "rss",
        version=version)

    channel = etree.SubElement(root, "channel")
    title = etree.SubElement(channel, "title")
    title.text = title_text
    link = etree.SubElement(channel, "link")
    link.text = link_text
    description = etree.SubElement(channel, "description")
    description.text = description_text

    for i in enumerate(dataset['articleIds']):
        item = etree.SubElement(channel, "item")
        item_title = etree.SubElement(item, "title")
        item_title.text = list(
            dataset['articleTitles'])[i[0]].encode('ascii', 'xmlcharrefreplace')

        item_link = etree.SubElement(item, "link")
        item_link.text = list(
            dataset['articleUrls'])[i[0]].encode('ascii', 'xmlcharrefreplace')

        item_description = etree.SubElement(item, "description")
        item_description.text = list(dataset['articleHeaders'])[i[0]].encode('ascii', 'xmlcharrefreplace')

    return(etree.ElementTree(root))
