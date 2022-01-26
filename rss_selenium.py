
import os
from time import sleep

from selenium import webdriver  # sudo apt install python3-selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.support.ui import WebDriverWait as Wait

import rss_config
import rss_print

def get_service_log_path(articleUrl):
    if rss_config.PRINT_MESSAGE_LEVEL > 0:
        serviceLogPath = "/tmp/webdriver_" + articleUrl.replace("/", "|") + ".log"
        rss_print.print_debug(__file__, "logime asukohta: " + serviceLogPath, 0)
    else:
        os.environ['MOZ_HEADLESS'] = '1'
        serviceLogPath = os.devnull

    return serviceLogPath


def get_article_string(articleUrl, clicks, searchXpath, profile):
    """
    Use firefox to get page with javascript generated content.
    https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.firefox.options
    """
    rss_print.print_debug(__file__, "selenium internetipäring: " + articleUrl, 0)
    serviceLogPath = get_service_log_path(articleUrl)

    if profile is True:
        rss_print.print_debug(__file__, "kasutaja firefox profiil: " + rss_config.PATH_FIREFOX_PROFILE, 1)
        profile = webdriver.FirefoxProfile(rss_config.PATH_FIREFOX_PROFILE)
        rss_config.SELENIUM_DRIVER_PROFILE = webdriver.Firefox(executable_path=rss_config.PATH_WEBDRIVER, service_log_path=serviceLogPath, firefox_profile=profile)
        driver = rss_config.SELENIUM_DRIVER_PROFILE
    else:
        rss_print.print_debug(__file__, "seleniumi default profiil", 1)
        if not rss_config.SELENIUM_DRIVER_DEFAULT:
            rss_print.print_debug(__file__, "avame uue brauseri akna", 1)
            rss_config.SELENIUM_DRIVER_DEFAULT = webdriver.Firefox(executable_path=rss_config.PATH_WEBDRIVER, service_log_path=serviceLogPath)
            if rss_config.PRINT_MESSAGE_LEVEL < 2:
                rss_print.print_debug(__file__, "minimeerime akna: " + articleUrl, 3)
                rss_config.SELENIUM_DRIVER_DEFAULT.minimize_window()
        else:
            rss_print.print_debug(__file__, "kasutame avatud brauseri akent", 1)

        driver = rss_config.SELENIUM_DRIVER_DEFAULT

    try:
        rss_print.print_debug(__file__, "pärime lingi: " + articleUrl, 1)
        driver.get(articleUrl)

        driver.implicitly_wait(rss_config.REQUEST_TIMEOUT)  # seconds

        rss_print.print_debug(__file__, "liigume lehe lõppu: " + articleUrl, 1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        if "lineageos" in articleUrl:
            sleep(2)

        for click in clicks:
            sleep(0.1)  # 100 ms
            rss_print.print_debug(__file__, "teeme kliki: " + click, 1)
            driver.find_element_by_xpath(click).click()

        rss_print.print_debug(__file__, "ootame elementi: " + searchXpath, 1)
        Wait(driver, 20).until(cond.visibility_of_element_located((By.XPATH, searchXpath)))
        rss_print.print_debug(__file__, "ootasime elemendi: " + searchXpath, 1)

        rss_print.print_debug(__file__, "võtame lehelt 'page_source': " + searchXpath, 1)
        htmlPageString = driver.page_source
    except Exception as e:
        rss_print.print_debug(__file__, "selenium ei saanud lehte kätte", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e).replace("\n", "") + "'", 0)
        htmlPageString = ""

    return htmlPageString
