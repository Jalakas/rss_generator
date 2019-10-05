#!/usr/bin/env python3

from contextlib import closing
from selenium import webdriver  # sudo apt install python3-selenium

import parsers_common
import rss_config
import rss_print


def fill_article_dict(articleDataDict, pageTree, domain, articleUrl, session):

    # use firefox to get page with javascript generated content
    try:
        with closing(webdriver.Firefox(executable_path=rss_config.WEBDRIVER_PATH)) as driver:
            driver.get(articleUrl)
            driver.minimize_window()
            driver.find_element_by_xpath('//input[@name="starting_time" and @value="2"]').click()
            driver.find_element_by_xpath('//a[@data-view="list-view"]').click()
            driver.implicitly_wait(5)  # seconds
            driver.find_element_by_xpath('//div[@class="col-12"]/h1[@class="py-3"]')

            pageTree = parsers_common.html_tree_from_string(driver.page_source, articleUrl)
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
