
"""
    HTML-i hankimine.
"""

import parsers_html
import rss_config
import rss_disk
import rss_print
import rss_requests
import rss_selenium


def get_url_from_internet(curDomainLong, stamp, seleniumPath="", seleniumProfile=False):
    rss_print.print_debug(__file__, "algatame internetipäringu: " + curDomainLong, 3)

    seleniumClicks = ()

    # selenium
    if "auto24.ee" in curDomainLong:
        seleniumPath = '//div[@class="section messages"]'
    elif "arhiiv.err.ee" in curDomainLong:
        seleniumPath = '//app-card'
    elif "err.ee/uudised" in curDomainLong:
        seleniumPath = '//div[@class="ng-scope"]'
    elif "kultuuriaken.tartu.ee/et/syndmused" in curDomainLong:
        seleniumClicks = (
            '//input[@name="starting_time" and @value="2"]',
            '//a[@data-view="list-view"]',
            )
        seleniumPath = '/html/body/div[2]/section/div/div[3]/div[2]/div[4]/div[2]/div/div/div[2]'
    elif "mixcloud.com" in curDomainLong:
        seleniumPath = '//main/div[@class="content"]/div/div/div'
    elif "osta.ee" in curDomainLong:
        seleniumPath = '//article/ul/li/figure'

    # teeme päringu
    if seleniumPath or seleniumClicks or "treraadio.ee" in curDomainLong or "twitter.com" in curDomainLong:
        htmlPageString = rss_selenium.get_article_string(curDomainLong, seleniumClicks, seleniumPath, seleniumProfile)
    else:
        htmlPageString = rss_requests.get_article_string(curDomainLong, rss_config.HEADERS)

    # puhastame lehe üleliigsest jamast
    htmlPageString = parsers_html.html_page_cleanup(htmlPageString)

    # salvestame kõikide netipäringute tulemused alati kettale
    if stamp:
        rss_disk.write_file_string_to_cache(curDomainLong + "#" + stamp, htmlPageString)
    else:
        rss_disk.write_file_string_to_cache(curDomainLong, htmlPageString)

    return htmlPageString
