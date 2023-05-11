
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

    # selenium configuraton
    # Ei lae ilma Javascriptita üldse lehte
    if "arhiiv.err.ee" in curDomainLong:
        seleniumPath = '//app-grid[@class="ng-star-inserted"]'
    # Ei lae ilma Javascriptita foorumit
    elif "auto24.ee/foorum" in curDomainLong:
        seleniumPath = '//div[@class="section messages"]'
    # Ei lae ilma Javascriptita uudiseid
    elif "err.ee/uudised" in curDomainLong:
        seleniumPath = '//div[@class="ng-scope"]'
    # "Võimalik tõrge teie veebilehitsejas"
    elif "osta.ee/kategooria" in curDomainLong:
        seleniumPath = '//article/ul/li/figure'
    # Ei lae ilma Javascriptita uudiseid
    elif "keskeesti.treraadio.ee/uudised" in curDomainLong:
        seleniumPath = '/html'

    # teeme päringu
    if rss_config.SELENIUM_POLICY == 'all':
        htmlPageString = rss_selenium.get_article_string(curDomainLong, seleniumClicks, seleniumPath, seleniumProfile)
    elif rss_config.SELENIUM_POLICY == 'auto' and (seleniumPath or seleniumClicks  ):
        htmlPageString = rss_selenium.get_article_string(curDomainLong, seleniumClicks, seleniumPath, seleniumProfile)
    elif rss_config.SELENIUM_POLICY == 'auto':
        htmlPageString = rss_requests.get_article_string(curDomainLong, rss_config.HEADERS)
    elif rss_config.SELENIUM_POLICY == 'off':
        htmlPageString = rss_requests.get_article_string(curDomainLong, rss_config.HEADERS)

    # puhastame lehe üleliigsest jamast
    htmlPageString = parsers_html.html_page_cleanup(htmlPageString)

    # salvestame kõikide netipäringute tulemused alati kettale
    if stamp:
        rss_disk.write_file_string_to_cache(curDomainLong + "#" + stamp, htmlPageString)
    else:
        rss_disk.write_file_string_to_cache(curDomainLong, htmlPageString)

    return htmlPageString
