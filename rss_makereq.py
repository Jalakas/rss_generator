#!/usr/bin/env python3

"""
    HTML-i hankimine
"""

import requests

import parsers_common
import rss_config
import rss_print
import rss_selenium
import rss_disk


def get_url_as_html_string(session, articleUrl):
    """
    Päringu teostamine HTML-i allalaadimiseks
    Väljund: unicode kodeeringus string
    """

    htmlPageString = ""

    try:
        htmlPage = session.get(articleUrl, headers=rss_config.HEADERS, timeout=rss_config.TIMEOUT)
        htmlPageBytes = htmlPage.content
        htmlPageBytesEncoding = htmlPage.encoding
    except Exception as e:
        rss_print.print_debug(__file__, "internetipäring EBAõnnestus, tagastame tühja vastuse", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        return htmlPageString

    # proovime baitide dekodeerise 'kaasapandud' vormingust
    try:
        htmlPageString = parsers_common.decode_bytes_to_str(htmlPageBytes, htmlPageBytesEncoding)
    except Exception as e:
        rss_print.print_debug(__file__, "internetipäringu tulemuse dekodeerimine '" + htmlPageBytesEncoding + "' kujul EBAõnnestus", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

        # proovime baitide dekodeerimist 'väljapakutud' vormingust
        htmlPageBytesEncodingApparent = htmlPage.apparent_encoding
        rss_print.print_debug(__file__, "proovime dekoodida 'apparent' vormingus '" + htmlPageBytesEncodingApparent + "'", 0)
        htmlPageString = parsers_common.decode_bytes_to_str(htmlPageBytes, htmlPageBytesEncodingApparent)
        rss_print.print_debug(__file__, "internetipäringu tulemuse dekodeerimine '" + htmlPageBytesEncodingApparent + "' kujul õnnestus", 0)

    return htmlPageString


def get_url_string_from_internet(session, curDomainShort, curDomainLong):

    rss_print.print_debug(__file__, "internetipäring: " + curDomainLong, 0)

    clicks = []
    if "kultuuriaken" in curDomainShort:
        rss_print.print_debug(__file__, "teeme seleniumi päringu, kuna leht: " + curDomainShort, 2)
        clicks = ['//input[@name="starting_time" and @value="2"]', '//a[@data-view="list-view"]']
        htmlPageString = rss_selenium.get_article_string_from_browser(curDomainLong, clicks, '//div[@class="col-12"]/h1[@class="py-3"]', profile=False)
    elif "lineageos" in curDomainShort:
        rss_print.print_debug(__file__, "teeme seleniumi päringu, kuna leht: " + curDomainShort, 2)
        htmlPageString = rss_selenium.get_article_string_from_browser(curDomainLong, clicks, '//li[@class="collection-item flex-dynamic"]', profile=False)
    elif "tv3" in curDomainShort:
        rss_print.print_debug(__file__, "teeme seleniumi päringu, kuna leht: " + curDomainShort, 2)
        htmlPageString = rss_selenium.get_article_string_from_browser(curDomainLong, clicks, '//a[@class="sc-1kym84g-0 dxESGf c950ig-0 eUNpOJ"]', profile=False)
    elif "youtube" in curDomainShort:
        rss_print.print_debug(__file__, "teeme seleniumi päringu, kuna leht: " + curDomainShort, 2)
        htmlPageString = rss_selenium.get_article_string_from_browser(curDomainLong, clicks, '//a[@id="video-title"]', profile=True)
    else:
        rss_print.print_debug(__file__, "teeme tavalise päringu, kuna leht: " + curDomainShort, 2)
        htmlPageString = get_url_as_html_string(session, curDomainLong)

    # kodeeringuprobleemide kontroll
    if (htmlPageString.find("Ã¤") >= 0 or htmlPageString.find("Ãµ") >= 0):
        pos = max(htmlPageString.find("Ã¤"), htmlPageString.find("Ãµ"))
        rss_print.print_debug(__file__, "'Ã' tüüpi kodeering asukohas(" + str(pos) + "): '" + htmlPageString[pos - 20:pos + 20] + "', proovime parandada", 1)
        htmlPageString = parsers_common.fix_broken_encoding_as_encoding_string(htmlPageString, 'utf-8', 'iso8859_1')

    # ~ if (htmlPageString.find("Ã¤") >= 0 or htmlPageString.find("Ãµ") >= 0) and htmlPageBytesEncoding == "ISO-8859-1":
        # ~ pos = max(htmlPageString.find("Ã¤"), htmlPageString.find("Ãµ"))
        # ~ rss_print.print_debug(__file__, "päringu tulemuse formaat htmlPage.encoding: '" + htmlPageBytesEncoding + "'", 0)
        # ~ rss_print.print_debug(__file__, "'Ã' tüüpi kodeering asukohas(" + str(pos) + "): '" + htmlPageString[pos - 20:pos + 20] + "', proovime parandada", 0)
        # ~ htmlPageString = decode_bytes_to_str(htmlPageBytes, 'utf-8')

    if (htmlPageString.find("¦") >= 0 or htmlPageString.find("¸") >= 0):
        # https://www.i18nqa.com/debug/table-iso8859-1-vs-iso8859-15.html
        # "¤" ja "´" on levinud sümbol ja ei viita katustega ess-ide kodeeringu probleemile
        pos = max(htmlPageString.find("¦"), htmlPageString.find("¸"))
        rss_print.print_debug(__file__, "'iso8859_15 as iso8859_1' kodeering asukohas(" + str(pos) + "): '" + htmlPageString[pos - 20:pos + 20] + "', proovime parandada", 0)
        htmlPageString = parsers_common.fix_broken_encoding_as_encoding_string(htmlPageString, 'iso8859_15', 'iso8859_1')

    if htmlPageString.find("&#") >= 0:
        pos = htmlPageString.find("&#")
        rss_print.print_debug(__file__, "'&#' tüüpi kodeering asukohas(" + str(pos) + "): '" + htmlPageString[pos - 20:pos + 20] + "', proovime parandada", 3)
        htmlPageString = parsers_common.unescape(htmlPageString)

    # salvestame kõikide netipäringute tulemused alati kettale
    rss_disk.write_file_string_to_cache(curDomainLong, htmlPageString)

    return htmlPageString


def upload_file(filePath, filename):
    filePathFull = filePath + "/" + filename
    rss_print.print_debug(__file__, "asume üles laadima faili: " + filePathFull, 3)

    try:
        curFile = open(filePathFull, 'rb')
        files = {rss_config.UPLOAD_NAME: curFile}
        reply = requests.post(rss_config.UPLOAD_URL, files=files)
        replyStatusCode = reply.status_code

        if replyStatusCode == 200:
            rss_print.print_debug(__file__, "faili üleslaadimine õnnestus: " + filename, 3)
            rss_print.print_debug(__file__, "serveri vastus: reply.status_code = " + str(replyStatusCode), 4)
        else:
            rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + filename, 0)
            rss_print.print_debug(__file__, "serveri vastus: reply.status_code = " + str(replyStatusCode), 1)
    except Exception as e:
        rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + filename, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
