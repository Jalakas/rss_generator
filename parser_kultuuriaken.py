#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Kultuuriaken RSS-voo sisendite parsimine
"""

from contextlib import closing
from selenium.webdriver import Firefox  # sudo apt install python3-selenium
import time
from lxml import html

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit, getArticleBodies):
    """
    Meetod saidi kõigi uudiste nimekirja loomiseks
    """

    url = 'https://kultuuriaken.tartu.ee/et/syndmused?category_1=all|40|41|42|43|44|52&category_2=all|45|46|47|48|49|50|51|53&category_7=all&category_3=all&category_8=all&category_54=all&category_4=all&category_5=all&category_6=all&category_9=all&region=Tartu|78|LE&starting_time=2&filter-button=9#'

    # use firefox to get page with javascript generated content
    with closing(Firefox(executable_path=r"/home/anari/rss_generator/geckodriver")) as browser:
        browser.get(url)
        time.sleep(6)
        pageTree = html.fromstring(browser.page_source)

    articleDescriptions = []
    articleImages = parsers_common.xpath(pageTree, '//div[@class="list-item"]/a[@class="image"]/@style')
    articlePubDates = []
    articleTitles = parsers_common.xpath(pageTree, '//div[@class="list-item"]/div[@class="details"]/a[1]/text()')
    articleUrls = parsers_common.xpath(pageTree, '//div[@class="list-item"]/div[@class="details"]/a[1]/@href')

    articleDescriptionsParents = parsers_common.xpath(pageTree, '//div[@class="list-item"]/div[@class="details"]')  # as a parent

    for i in range(0, min(len(articleUrls), maxPageURLstoVisit)):
        # description
        articleDescriptions.append(parsers_common.stringify_children(articleDescriptionsParents[i]))

        # image
        articleImages[i] = articleImages[i].split("'")[1]

        # url
        articleUrls[i] = articleUrls[i].split("?event=")[0]

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
