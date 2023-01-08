
import os
from time import sleep

from selenium import webdriver  # sudo apt install python3-selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

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


def generate_driver(articleUrl, profile):
    rss_print.print_debug(__file__, "genereerime sessiooni uue brauseri akna", 1)

    serviceLogPath = get_service_log_path(articleUrl)

    options = Options()
    if rss_config.PRINT_MESSAGE_LEVEL < 2:
        rss_print.print_debug(__file__, "aken on varjatud", 1)
        options.headless = True

    if profile is True:
        rss_print.print_debug(__file__, "seleniumi profiil on määratud: " + rss_config.PATH_FIREFOX_PROFILE, 1)
        profile = webdriver.FirefoxProfile(rss_config.PATH_FIREFOX_PROFILE)

        rss_print.print_debug(__file__, "genereerime uue brauseri akna profiilist", 1)
        driver = webdriver.Firefox(
            firefox_profile=profile,
            executable_path=rss_config.PATH_WEBDRIVER,
            options=options,
            service_log_path=serviceLogPath
        )
    else:
        rss_print.print_debug(__file__, "seleniumi profiil on määramata", 1)

        rss_print.print_debug(__file__, "genereerime uue brauseri akna vaikimeseadetega", 1)
        driver = webdriver.Firefox(
            executable_path=rss_config.PATH_WEBDRIVER,
            options=options,
            service_log_path=serviceLogPath
        )

    rss_print.print_debug(__file__, "maksimeerime akna", 1)
    driver.maximize_window()

    # nii profiiliga või profiilita olukorras peame määrama timeouti ja akna suuruse
    rss_print.print_debug(__file__, "määrame ootamise timeoudi", 1)
    driver.implicitly_wait(rss_config.REQUEST_TIMEOUT)  # seconds

    return driver


def get_article_string(articleUrl, clicks, searchXpath, profile):
    """
    Use firefox to get page with javascript generated content.
    https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.firefox.options
    """
    rss_print.print_debug(__file__, "selenium internetipäring: " + articleUrl, 0)

    if rss_config.SELENIUM_DRIVER:
        rss_print.print_debug(__file__, "kasutame sessiooni vana brauseri akent", 1)
    else:
        rss_config.SELENIUM_DRIVER = generate_driver(articleUrl, profile)
    driver = rss_config.SELENIUM_DRIVER

    rss_print.print_debug(__file__, "pärime põhitabis lingi: " + articleUrl, 1)
    try:
        driver.get(articleUrl)
    except Exception as e:
        rss_print.print_debug(__file__, "pärime põhitabis lingi: ebaõnnestus", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e).replace("\n", "") + "'", 0)

    # try:
        # rss_print.print_debug(__file__, "liigume lehe lõppu: " + articleUrl, 1)
        # driver.execute_script("window.scrollTo(0, 1000);")
    # except Exception as e:
        # rss_print.print_debug(__file__, "liigume lehe lõppu: ebaõnnestus", 0)
        # rss_print.print_debug(__file__, "exception = '" + str(e).replace("\n", "") + "'", 0)

    try:
        for click in clicks:
            sleep(0.1)  # 100 ms
            rss_print.print_debug(__file__, "teeme kliki: " + click, 1)
            driver.find_element(By.XPATH, click).click()
    except Exception as e:
        rss_print.print_debug(__file__, "teeme kliki: ebaõnnestus", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e).replace("\n", "") + "'", 0)

    if not searchXpath:
        rss_print.print_debug(__file__, "ootamise element on määramata: " + articleUrl, 1)
    else:
        rss_print.print_debug(__file__, "ootame elementi: " + searchXpath, 1)
        try:
            WebDriverWait(driver, rss_config.REQUEST_TIMEOUT).until(expected_conditions.visibility_of_element_located((By.XPATH, searchXpath)))
        except Exception as e:
            rss_print.print_debug(__file__, "ootame elementi: ebaõnnestus", 0)
            rss_print.print_debug(__file__, "exception = '" + str(e).replace("\n", "") + "'", 0)
        rss_print.print_debug(__file__, "ootasime ära elemendi: " + searchXpath, 1)

    rss_print.print_debug(__file__, "võtame lehelt 'page_source': " + articleUrl, 1)
    try:
        htmlPageString = driver.page_source
    except Exception as e:
        htmlPageString = ""
        rss_print.print_debug(__file__, "võtame lehelt 'page_source': ebaõnnestus", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e).replace("\n", "") + "'", 0)

    return htmlPageString
