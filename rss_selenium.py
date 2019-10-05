#!/usr/bin/env python3

from contextlib import closing
from selenium import webdriver  # sudo apt install python3-selenium

import parsers_common
import rss_config
import rss_print


def get_article_tree_from_browser(articleUrl, searchXpath):

    # use firefox to get page with javascript generated content
    try:
        with closing(webdriver.Firefox(executable_path=rss_config.WEBDRIVER_PATH)) as driver:
            driver.get(articleUrl)
            driver.minimize_window()
            driver.find_element_by_xpath(searchXpath)

            pageTree = parsers_common.html_tree_from_string(driver.page_source, articleUrl)

    except Exception as e:
        rss_print.print_debug(__file__, "ei saand vaiervokksi käima, katkestame seleniumiga pärimise", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

    return pageTree
