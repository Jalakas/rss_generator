#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from contextlib import closing
from selenium import webdriver  # sudo apt install python3-selenium
from lxml import html

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, session):

    url = 'https://kultuuriaken.tartu.ee/et/syndmused?category_1=all|40|41|42|43|44|52&category_2=all|45|46|47|48|49|50|51|53&category_7=all&category_3=all&category_8=all&category_54=all&category_4=all&category_5=all&category_6=all&category_9=all&region=Tartu|78|LE&starting_time=2&filter-button=9#'

    # use firefox to get page with javascript generated content
    try:
        with closing(webdriver.Firefox(executable_path=rss_config.WEBDRIVER_PATH)) as driver:
            driver.get(url)
            driver.find_element_by_xpath('//input[@name="starting_time" and @value="2"]').click()
            driver.find_element_by_xpath('//a[@data-view="list-view"]').click()
            driver.implicitly_wait(5)  # seconds
            driver.find_element_by_xpath('//div[@class="col-12"]/h1[@class="py-3"]')
            pageTree = html.fromstring(driver.page_source)
    except Exception as e:
        rss_print.print_debug(__file__, "ei saand vaiervokksi käima, katkestame seleniumiga pärimise", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

    articleDataDict["images"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/a[@class="image"]/@style')
    articleDataDict["titles"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]/a[1]/text()')
    articleDataDict["urls"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]/a[1]/@href')
    articleDataDict["descriptions"] = parsers_common.xpath_to_list(pageTree, '//div[@class="list-item"]/div[@class="details"]', parent=True)

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # image
        curArtImage = articleDataDict["images"][i]
        curArtImage = curArtImage.split("'")[1]
        articleDataDict["images"][i] = curArtImage

        # url
        curArtUrl = articleDataDict["urls"][i]
        curArtUrl = curArtUrl.split("?event=")[0]
        articleDataDict["urls"][i] = curArtUrl

    return articleDataDict
