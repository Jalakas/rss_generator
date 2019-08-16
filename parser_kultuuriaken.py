#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Kultuuriaken RSS-voo sisendite parsimine
"""

from contextlib import closing
from selenium import webdriver  # sudo apt install python3-selenium
from lxml import html

import parsers_common


def getArticleListsFromHtml(articleDataDict, pageTree, domain, maxArticleCount, getArticleBodies):

    url = 'https://kultuuriaken.tartu.ee/et/syndmused?category_1=all|40|41|42|43|44|52&category_2=all|45|46|47|48|49|50|51|53&category_7=all&category_3=all&category_8=all&category_54=all&category_4=all&category_5=all&category_6=all&category_9=all&region=Tartu|78|LE&starting_time=2&filter-button=9#'

    # use firefox to get page with javascript generated content
    try:
        with closing(webdriver.Firefox(executable_path=r"/home/anari/rss_generator/geckodriver")) as driver:
            driver.get(url)
            driver.find_element_by_xpath('//input[@name="starting_time" and @value="2"]').click()
            driver.find_element_by_xpath('//a[@data-view="list-view"]').click()
            driver.implicitly_wait(5)  # seconds
            driver.find_element_by_xpath('//div[@class="col-12"]/h1[@class="py-3"]')
            pageTree = html.fromstring(driver.page_source)
    except Exception:
        print("ei saand vaiervokksi käima")

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/a[@class="image"]/@style')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]/a[1]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]/a[1]/@href')

    articleDescriptionsParents = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]')  # as a parent

    for i in parsers_common.articleUrlsRange(articleDataDict["urls"]):
        # description
        curArtDescChilds = parsers_common.stringify_index_children(articleDescriptionsParents, i)
        articleDataDict["descriptions"].append(curArtDescChilds)

        # image
        articleDataDict["images"][i] = articleDataDict["images"][i].split("'")[1]

        # url
        articleDataDict["urls"][i] = articleDataDict["urls"][i].split("?event=")[0]

    return articleDataDict
