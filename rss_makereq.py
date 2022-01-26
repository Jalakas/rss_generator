
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
    rss_print.print_debug(__file__, "algatame internetipäringu: " + curDomainLong, 2)

    seleniumClicks = []

    # selenium
    if "auto24.ee" in curDomainLong:
        seleniumPath = '//div[@class="section messages"]'
    elif "err.ee/uudised" in curDomainLong:
        seleniumPath = '//div[@class="ng-scope"]'
    elif "kultuuriaken.tartu.ee/et/syndmused" in curDomainLong:
        seleniumClicks = ['//input[@name="starting_time" and @value="2"]', '//a[@data-view="list-view"]']
        seleniumPath = '//div[@class="col-12"]/h1[@class="py-3"]'
    elif "levila.ee" in curDomainLong:
        seleniumPath = '//a[@class="post-item-meta__link"]'
    elif "mixcloud.com" in curDomainLong:
        seleniumPath = '//main/div[@class="content"]/div/div/div'
    elif "sky.ee" in curDomainLong:
        seleniumPath = '//div[@class="box-news-block-title "]'
    elif "treraadio.ee" in curDomainLong:
        seleniumPath = '//a[@id="scrollBtn"]'
    elif "tv3.ee" in curDomainLong:
        seleniumPath = '//a[@class="sc-1kym84g-0 dxESGf c950ig-0 eUNpOJ"]'
    elif "twitter.com" in curDomainLong:
        seleniumPath = '//article[@role="article"]'

    # teeme päringu
    if seleniumPath:
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
