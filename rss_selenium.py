#!/usr/bin/env python3

import os
from time import sleep

from contextlib import closing
from selenium import webdriver  # sudo apt install python3-selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as cond

import rss_config
import rss_print


def get_article_string_from_browser(articleUrl, clicks, searchXpath, profile):

    pageHtmlString = ""

    # use firefox to get page with javascript generated content
    try:
        if profile is True:
            rss_print.print_debug(__file__, "kasutame profiili: " + rss_config.PATH_PROFILE_FIREFOX, 1)
            profile = webdriver.FirefoxProfile(rss_config.PATH_PROFILE_FIREFOX)
            webdriverFirefox = webdriver.Firefox(executable_path=rss_config.PATH_WEBDRIVER, service_log_path=os.devnull, firefox_profile=profile)
        else:
            webdriverFirefox = webdriver.Firefox(executable_path=rss_config.PATH_WEBDRIVER, service_log_path=os.devnull)

        with closing(webdriverFirefox) as driver:
            driver.minimize_window()

            rss_print.print_debug(__file__, "pärime lingi: " + articleUrl, 1)
            driver.get(articleUrl)

            for click in clicks:
                sleep(0.1)  # 100 ms
                rss_print.print_debug(__file__, "teeme kliki: " + click, 1)
                driver.find_element_by_xpath(click).click()

            rss_print.print_debug(__file__, "ootame elementi: " + searchXpath, 1)
            wait(driver, 20).until(cond.visibility_of_element_located((By.XPATH, searchXpath)))
            rss_print.print_debug(__file__, "ootasime elemendi: " + searchXpath, 1)

            pageHtmlString = driver.page_source
    except Exception as e:
        rss_print.print_debug(__file__, "ei saand vaiervokksi käima? katkestame seleniumiga pärimise", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 0)

    rss_print.print_debug(__file__, "tagastame lehe stringi: " + articleUrl, 1)
    return pageHtmlString
