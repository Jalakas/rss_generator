
"""
    HTML-i hankimine.
"""

import html
import requests
import urllib3

import parsers_common
import rss_config
import rss_print

SESSION = requests.Session()
urllib3.disable_warnings()


def encoding_check(htmlPageString, htmlPageBytesEncoding):
    rss_print.print_debug(__file__, "kodeeringuprobleemide kontroll, sisend vormingus: '" + htmlPageBytesEncoding + "'", 3)

    pos = max(-1, htmlPageString.find("&#"))
    if pos >= 0:
        rss_print.print_debug(__file__, "'&#' tüüpi kodeering asukohas(" + str(pos) + "): '" + htmlPageString[pos - 10:pos + 30] + "', proovime parandada", 2)
        htmlPageString = html.unescape(htmlPageString)

    # https://www.i18nqa.com/debug/table-iso8859-1-vs-iso8859-15.html
    pos = max(-1, htmlPageString.find("Ã¤"), htmlPageString.find("Ãµ"))
    if pos >= 0:
        rss_print.print_debug(__file__, "'Ã_' tüüpi kodeering asukohas(" + str(pos) + "): '" + htmlPageString[pos - 10:pos + 30] + "', proovime parandada", 1)
        htmlPageString = encoding_fix_with_deencode(htmlPageString, 'utf-8', htmlPageBytesEncoding)

    # "¤´" on levinud sümbolid ja ei viita katustega ess-ide kodeeringu probleemile
    pos = max(-1, htmlPageString.find("¦"), htmlPageString.find("¨"), htmlPageString.find("¸"))
    if pos >= 0:
        rss_print.print_debug(__file__, "'iso8859_15 as iso8859_1' kodeering asukohas(" + str(pos) + "): '" + htmlPageString[pos - 10:pos + 30] + "', proovime parandada", 0)
        htmlPageString = encoding_fix_with_deencode(htmlPageString, 'iso8859_15', htmlPageBytesEncoding)

    return htmlPageString


def encoding_fix_with_deencode(inpString, sourceEncoding, destEncoding):
    """
    Imiteerime vigast "enkooding" -> "enkooding" konverteerimist ja asendame nii leitud sümbolid tagasi algseteks sümboliteks.
    näiteks: sourceEncoding='utf-8', destEncoding='iso8859_15'
    https://i18nqa.com/debug/UTF8-debug.html
    """
    rss_print.print_debug(__file__, "EBAõnnestunud '" + sourceEncoding + "' as '" + destEncoding + "' kodeeringu parandamine 'tagasiasendamisega'", 1)
    rss_print.print_debug(__file__, "'" + inpString + "'", 4)

    # handpicked changes
    inpString = inpString.replace('Ã¤', 'ä')
    inpString = inpString.replace('Ãµ', 'õ')
    inpString = inpString.replace('Ã¶', 'ö')
    inpString = inpString.replace('Ã¼', 'ü')
    inpString = inpString.replace('Ãœ', 'Ü')
    inpString = inpString.replace('Ã–', 'Ö')
    inpString = inpString.replace('Ã„', 'Ä')
    inpString = inpString.replace('Ã•', 'Õ')
    inpString = inpString.replace('â', '–')
    inpString = inpString.replace('â', '"')
    inpString = inpString.replace('â', '"')
    inpString = inpString.replace('â', '"')

    return inpString


def encoding_fix_with_replace(inpString):
    rss_print.print_debug(__file__, "parandame EBAõnnestunud kodeeringu asendamise läbi", 1)

    inpString = inpString.replace("\\\\x", "\\x")

    # handpicked changes
    inpString = inpString.replace("\\xc2\\xa0", " ")
    inpString = inpString.replace("\\xc2\\xab", '"')
    inpString = inpString.replace("\\xc2\\xbb", '"')
    inpString = inpString.replace('\\xc3\\x84', 'Ä')
    inpString = inpString.replace('\\xc3\\x95', 'Õ')
    inpString = inpString.replace('\\xc3\\x96', 'Ö')
    inpString = inpString.replace('\\xc3\\x97', '-')
    inpString = inpString.replace('\\xc3\\x9c', 'Ü')
    inpString = inpString.replace('\\xc3\\xa4', 'ä')
    inpString = inpString.replace('\\xc3\\xb5', 'õ')
    inpString = inpString.replace('\\xc3\\xb6', 'ö')
    inpString = inpString.replace('\\xc3\\xbc', 'ü')
    inpString = inpString.replace('\\xc3\\x83', 'Ã')  # viitab mitmekordsele kodeeringuprobleemile, juu aar fakt
    inpString = inpString.replace('\\xc3\\x85', 'Å')  # viitab mitmekordsele kodeeringuprobleemile, juu aar fakt
    inpString = inpString.replace("\\xe2\\x80\\x93", "–")
    inpString = inpString.replace('\\xc3\\xa9', 'é')
    inpString = inpString.replace('\\xe2\\x80\\x9d', '"')
    inpString = inpString.replace('\\xe2\\x80\\x9c', '"')

    rss_print.print_debug(__file__, "output='" + inpString + "'", 4)

    return inpString


def get_article_string(articleUrl, headers):
    """
    Päringu teostamine HTML-i allalaadimiseks.
    Väljund: unicode kodeeringus string
    """
    rss_print.print_debug(__file__, "tavaline internetipäring: " + articleUrl, 0)
    try:
        htmlPage = SESSION.get(articleUrl, headers=headers, timeout=rss_config.REQUEST_TIMEOUT, verify=False)  # pylint: disable=E1101
    except Exception as e:
        rss_print.print_debug(__file__, "internetipäring EBAõnnestus, tagastame tühja vastuse", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 0)
        return ""

    rss_print.print_debug(__file__, "kontrollime urli redirectimist: " + articleUrl, 4)
    htmlPageUrl = parsers_common.str_rchop(htmlPage.url, "/")
    if htmlPageUrl[0:5] != articleUrl[0:5]:
        rss_print.print_debug(__file__, "vastuse URLi algus erineb päringu URList: " + htmlPageUrl + "!=" + articleUrl, 0)

    rss_print.print_debug(__file__, "internetipäringu tulemuse dekodeerimine: " + articleUrl, 3)
    htmlPageBytes = htmlPage.content
    htmlPageBytesEncoding = htmlPage.encoding
    try:
        htmlPageString = parsers_common.bytes_to_str(htmlPageBytes, htmlPageBytesEncoding)
    except Exception as e:
        rss_print.print_debug(__file__, "internetipäringu tulemuse dekodeerimine '" + htmlPageBytesEncoding + "' kujul EBAõnnestus", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

        # proovime baitide dekodeerimist 'väljapakutud' vormingust
        rss_print.print_debug(__file__, "internetipäringu tulemuse dekodeerimine 'apparent' enkoodingus: " + articleUrl, 0)
        htmlPageBytesEncoding = htmlPage.apparent_encoding
        try:
            htmlPageString = parsers_common.bytes_to_str(htmlPageBytes, htmlPageBytesEncoding)
            rss_print.print_debug(__file__, "internetipäringu tulemuse dekodeerimine '" + htmlPageBytesEncoding + "' kujul õnnestus", 0)
        except Exception as e:
            rss_print.print_debug(__file__, "internetipäringu tulemuse dekodeerimine '" + htmlPageBytesEncoding + "' kujul EBAõnnestus", 0)
            rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

    htmlPageString = encoding_check(htmlPageString, htmlPageBytesEncoding)

    return htmlPageString


def upload_file(filePath, filename):
    filePathFull = filePath + "/" + filename
    rss_print.print_debug(__file__, "asume üles laadima faili: " + filePathFull, 3)

    try:
        with open(filePathFull, 'rb') as curFile:
            files = {rss_config.UPLOAD_NAME: curFile}
            reply = requests.post(rss_config.UPLOAD_URL, files=files, timeout=10)
            replyStatusCode = reply.status_code

            if replyStatusCode == 200:
                rss_print.print_debug(__file__, "faili üleslaadimine õnnestus: " + filename, 3)
                rss_print.print_debug(__file__, "serveri vastus: reply.status_code = " + str(replyStatusCode), 4)
            else:
                rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + filename, 0)
                rss_print.print_debug(__file__, "serveri vastus: reply.status_code = " + str(replyStatusCode), 1)
                rss_print.print_debug(__file__, "serveri vastus: reply.text = " + str(reply.text), 2)
    except Exception as e:
        rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + filename, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
