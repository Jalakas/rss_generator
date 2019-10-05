#!/usr/bin/env python3

"""
    HTML-i hankimine
"""

from html import unescape
import requests

import parsers_common
import rss_config
import rss_disk
import rss_print


def get_url_as_html_string(session, articleUrl):
    """
    Päringu teostamine HTML-i allalaadimiseks
    Väljund: unicode kodeeringus string
    """

    rss_print.print_debug(__file__, "teeme internetipäringu lehele: " + articleUrl, 0)

    htmlPageString = ""

    try:
        htmlPage = session.get(articleUrl, headers=rss_config.HEADERS, timeout=10)
        htmlPageBytes = htmlPage.content
        htmlPageBytesEncoding = htmlPage.encoding
    except Exception as e:
        rss_print.print_debug(__file__, "päring ebaõnnestus, tagastame tühja vastuse", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        return htmlPageString

    # proovime baitide dekodeerise 'kaasapandud' vormingust
    try:
        htmlPageString = parsers_common.decode_bytes_to_str(htmlPageBytes, htmlPageBytesEncoding)
    except Exception as e:
        rss_print.print_debug(__file__, "päringu tulemuse dekodeerimine '" + htmlPageBytesEncoding + "' kujul ebaõnnestus", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        # proovime baitide dekodeerimist 'väljapakutud' vormingust
        htmlPageBytesEncodingApparent = htmlPage.apparent_encoding
        rss_print.print_debug(__file__, "proovime dekoodida 'apparent' vormingus '" + htmlPageBytesEncodingApparent + "'", 0)
        htmlPageString = parsers_common.decode_bytes_to_str(htmlPageBytes, htmlPageBytesEncodingApparent)
        rss_print.print_debug(__file__, "päringu tulemuse dekodeerimine '" + htmlPageBytesEncodingApparent + "' kujul õnnestus", 0)

    # kodeeringuprobleemide kontroll

    if (htmlPageString.find("Ã¤") >= 0 or htmlPageString.find("Ãµ") >= 0):
        pos = max(htmlPageString.find("Ã¤"), htmlPageString.find("Ãµ"))
        rss_print.print_debug(__file__, "päringu tulemuse formaat htmlPage.encoding: '" + htmlPageBytesEncoding + "'", 1)
        rss_print.print_debug(__file__, "'Ã' tüüpi kodeering asukohas(" + str(pos) + "): '" + str(htmlPageString[pos - 20:pos + 20]) + "', proovime parandada", 1)
        htmlPageString = parsers_common.fix_broken_encoding_as_encoding_string(htmlPageString, 'utf-8', 'iso8859_1')

    # ~ if (htmlPageString.find("Ã¤") >= 0 or htmlPageString.find("Ãµ") >= 0) and htmlPageBytesEncoding == "ISO-8859-1":
        # ~ pos = max(htmlPageString.find("Ã¤"), htmlPageString.find("Ãµ"))
        # ~ rss_print.print_debug(__file__, "päringu tulemuse formaat htmlPage.encoding: '" + htmlPageBytesEncoding + "'", 0)
        # ~ rss_print.print_debug(__file__, "'Ã' tüüpi kodeering asukohas(" + str(pos) + "): '" + str(htmlPageString[pos - 20:pos + 20]) + "', proovime parandada", 0)
        # ~ htmlPageString = parsers_common.decode_bytes_to_str(htmlPageBytes, 'utf-8')

    if (htmlPageString.find("¦") >= 0 or htmlPageString.find("¨") >= 0 or htmlPageString.find("¸") >= 0):
        # https://www.i18nqa.com/debug/table-iso8859-1-vs-iso8859-15.html
        # '¤' kontrollime hiljem, "´" on levinud sümbol ja ei viita katustega ess-ide probleemile
        pos = max(htmlPageString.find("¦"), htmlPageString.find("¨"), htmlPageString.find("¸"))
        rss_print.print_debug(__file__, "päringu tulemuse formaat htmlPage.encoding: '" + htmlPageBytesEncoding + "'", 0)
        rss_print.print_debug(__file__, "'iso8859_15 as iso8859_1' kodeering asukohas(" + str(pos) + "): '" + str(htmlPageString[pos - 20:pos + 20]) + "', proovime parandada", 0)
        htmlPageString = parsers_common.fix_broken_encoding_as_encoding_string(htmlPageString, 'iso8859_15', 'iso8859_1')

    if htmlPageString.find("&#") >= 0:
        pos = htmlPageString.find("&#")
        rss_print.print_debug(__file__, "päringu tulemuse formaat htmlPage.encoding: '" + htmlPageBytesEncoding + "'", 1)
        rss_print.print_debug(__file__, "'&#' tüüpi kodeering asukohas(" + str(pos) + "): '" + str(htmlPageString[pos - 20:pos + 20]) + "', proovime parandada", 1)
        htmlPageString = unescape(htmlPageString)

    # salvestame kõikide netipäringute tulemused alati kettale
    rss_disk.write_file_string_to_cache(articleUrl, htmlPageString)

    return htmlPageString


def upload_file(curFilename, curFilenameFull):
    try:
        curFile = open(curFilenameFull, 'rb')
        files = {rss_config.UPLOAD_NAME: curFile}
        reply = requests.post(rss_config.UPLOAD_URL, files=files)
        replyStatusCode = reply.status_code

        rss_print.print_debug(__file__, "reply.status_code: " + str(replyStatusCode), 3)

        if replyStatusCode == 200:
            rss_print.print_debug(__file__, "faili üleslaadimine õnnestus: " + curFilename, 3)
        else:
            rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + curFilename, 0)
            rss_print.print_debug(__file__, "serveri vastus: " + str(reply.text), 2)
    except Exception as e:
        rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + curFilename, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
