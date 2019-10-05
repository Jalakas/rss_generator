#!/usr/bin/env python3

"""
    Erinevate parserid ja funktsioonid
"""

from datetime import datetime
from datetime import timedelta
from email import utils
from lxml import html
import re
import time

import rss_config
import rss_disk
import rss_makereq
import rss_print


def add_missing_date_to_string(curDatetimeString, fullDatetimeFormat, addedDateFormat):
    if len(curDatetimeString) < len(fullDatetimeFormat):
        curDatetimeString = add_to_time_string(curDatetimeString, addedDateFormat)
        rss_print.print_debug(__file__, "lisasime ajale 'kuupäeva' osa: " + curDatetimeString, 3)

    return curDatetimeString


def add_to_time_string(curArtPubDate, curDateFormat):
    curArtPubDate = datetime.now().strftime(curDateFormat) + curArtPubDate
    rss_print.print_debug(__file__, "lisasime tänasele kellaajale kuupäeva: " + curArtPubDate, 3)

    return curArtPubDate


def article_data_dict_clean(articleDataDict, dictField, dictCond, dictWhitelist=[], dictBlacklist=[]):
    if dictWhitelist:
        rss_print.print_debug(__file__, "kontrollime 'whitelist' kandeid", 2)
        curList = dictWhitelist
        condForDel = False
    elif dictBlacklist:
        rss_print.print_debug(__file__, "kontrollime 'blacklist' kandeid", 2)
        curList = dictBlacklist
        condForDel = True

    # asume kandeid kontrollima
    articleDictRange = range(len(curList))
    i = 0
    while i < len(articleDataDict[dictField]):
        curArticleDictElem = articleDataDict[dictField][i]
        rss_print.print_debug(__file__, "kontrollime kannet(" + str(i + 1) + "/" + str(len(articleDataDict[dictField])) + "): " + curArticleDictElem[0:100], 3)

        found = False
        for j in articleDictRange:
            curListElem = curList[j]
            if dictCond == "in":
                if curListElem in curArticleDictElem:
                    found = True
                    break
            elif dictCond == "==":
                if curListElem == curArticleDictElem:
                    found = True
                    break

        # kontrollime eemaldamistingimusele vastamist
        if found is condForDel:
            articleDataDict = del_article_dict_index(articleDataDict, i)
        else:
            i += 1

    return articleDataDict


def article_posts_range(articlePosts, maxArticlePostsCount):
    """
    Viimasest tagasi kuni piirarvu täitumiseni
    """
    articlePostsLen = len(articlePosts)
    rss_print.print_debug(__file__, 'xpath parsimisel leitud artikli poste: ' + str(articlePostsLen), 2)
    retRange = range(max(0, articlePostsLen - maxArticlePostsCount), articlePostsLen)

    return retRange


def article_urls_range(articleUrls):
    """
    Esimesest edasi kuni objektide lõpuni
    """
    articleUrlsLen = len(articleUrls)
    rss_print.print_debug(__file__, 'xpath parsimisel leitud artikleid: ' + str(articleUrlsLen), 2)
    retRange = range(articleUrlsLen)

    return retRange


def capitalize_first(inpString):
    inpString = inpString[0:1].capitalize() + inpString[1:]

    return inpString


def decode_bytes_to_str(inpBytes, inpEncoding):
    if isinstance(inpBytes, str):
        rss_print.print_debug(__file__, "sisend on juba string, tagastame sisendi", 0)
        return inpBytes

    try:
        retString = inpBytes.decode(inpEncoding)
    except Exception as e:
        rss_print.print_debug(__file__, "vaikimisi '" + inpEncoding + "' dekodeerimine ebaõnnestus, proovime vigade ignoreerimisega", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        retString = inpBytes.decode(inpEncoding, "replace")

    return retString


def del_article_dict_index(articleDataDict, k):
    rss_print.print_debug(__file__, "eemaldame mittesoovitud kande: '" + articleDataDict["titles"][k] + "'", 2)

    articleDataDict["authors"] = del_if_set(articleDataDict["authors"], k)
    articleDataDict["descriptions"] = del_if_set(articleDataDict["descriptions"], k)
    articleDataDict["images"] = del_if_set(articleDataDict["images"], k)
    articleDataDict["pubDates"] = del_if_set(articleDataDict["pubDates"], k)
    articleDataDict["titles"] = del_if_set(articleDataDict["titles"], k)
    articleDataDict["urls"] = del_if_set(articleDataDict["urls"], k)

    return articleDataDict


def del_if_set(inpList, inpIndex):
    inpListLen = len(inpList)
    indexHumanreadable = inpIndex + 1
    if inpListLen >= indexHumanreadable:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(inpListLen) + ", eemaldasime listi elemendi nr: " + str(indexHumanreadable), 4)
        del inpList[inpIndex]
    else:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(inpListLen) + ", ei eemaldand listi elementi nr: " + str(indexHumanreadable), 4)

    return inpList


def domain_url(domain, articleUrl):
    """
    Ühendab domeenid URLidega
    """
    articleUrl = domain.rstrip('/') + '/' + articleUrl.lstrip('./').lstrip('/')
    rss_print.print_debug(__file__, "pärast domeeni lisamist lingile: " + str(articleUrl), 4)

    return articleUrl


def fix_broken_encoding(inpString):

    rss_print.print_debug(__file__, "parandame ebaõnnestunud kodeeringu asendamise läbi", 1)
    rss_print.print_debug(__file__, "input inpString: '" + inpString + "'", 5)

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
    inpString = inpString.replace('\\xc3\\x83', 'Ã')  # viitab mitmekordsele kodderinguprobleemile, juu aar fakt
    inpString = inpString.replace('\\xc3\\x85', 'Å')  # viitab mitmekordsele kodderinguprobleemile, juu aar fakt
    inpString = inpString.replace("\\xe2\\x80\\x93", "–")
    inpString = inpString.replace('\\xc3\\xa9', 'é')
    inpString = inpString.replace('\\xe2\\x80\\x9d', '"')
    inpString = inpString.replace('\\xe2\\x80\\x9c', '"')

    rss_print.print_debug(__file__, "output inpString: '" + inpString + "'", 4)

    return inpString


def fix_broken_encoding_as_encoding_string(inpString, sourceEncoding, destEncoding):
    """
    Imiteerime vigast "enkooding" -> "enkooding" konverteerimist ja asendame nii leitud sümbolid tagasi algseteks sümboliteks
    näiteks: sourceEncoding='utf-8', destEncoding='iso8859_15'
    http://i18nqa.com/debug/UTF8-debug.html
    """

    rss_print.print_debug(__file__, "ebaõnnestunud '" + sourceEncoding + "' as '" + destEncoding + "' kodeeringu parandamine 'tagasiasendamisega'", 1)
    rss_print.print_debug(__file__, "inpString: '" + inpString + "'", 4)

    for curInt in range(0x80, 383):  # ž on 382 ja selle juures lõpetame
        sourceHex = hex(curInt)
        sourceSymbol = str(chr(curInt))

        try:
            destSymbol = sourceSymbol.encode(sourceEncoding)
            destSymbol = destSymbol.decode(destEncoding)
        except Exception as e:
            rss_print.print_debug(__file__, "i=" + str(sourceHex) + "\tsourceSymbol: '" + sourceSymbol + "'\t<->\tdestSymbol: pole sümbolit (" + str(e) + ")", 3)
            continue

        rss_print.print_debug(__file__, "i=" + str(sourceHex) + "\tsourceSymbol: '" + sourceSymbol + "'\t<->\tdestSymbol: '" + str(destSymbol) + "'", 4)

        inpString = inpString.replace(destSymbol, sourceSymbol)

    # handpicted changes
    inpString = inpString.replace('â', '"')
    inpString = inpString.replace('â', '"')
    inpString = inpString.replace('â', '–')
    inpString = inpString.replace('â', '"')

    rss_print.print_debug(__file__, "output inpString: '" + inpString + "'", 3)

    return inpString


def fix_drunk_post(drunkPostString):
    drunkPostString = rchop(drunkPostString, "<br>")
    drunkPostString = drunkPostString.strip()
    drunkPostString = drunkPostString.replace("   ", " ")
    drunkPostString = drunkPostString.replace("  ", " ")
    drunkPostString = drunkPostString + ". "

    # remove emoticons
    drunkPostString = drunkPostString.replace(" :", ": ").replace(":  ", ": ")
    drunkPostString = drunkPostString.replace(": (", "").replace(":(", "").replace(": (.", ".").replace(":(.", ".")
    drunkPostString = drunkPostString.replace(": )", "").replace(":)", "").replace(": ).", ".").replace(":).", ".")
    drunkPostString = drunkPostString.replace(": -(", "").replace(":-(", "").replace(": -(.", ".").replace(":-(.", ".")
    drunkPostString = drunkPostString.replace(": -)", "").replace(":-)", "").replace(": -).", ".").replace(":-).", ".")
    drunkPostString = drunkPostString.replace(": -D", "").replace(":-D", "").replace(": -D.", ".").replace(":-D.", ".")
    drunkPostString = drunkPostString.replace(": D ", " ").replace(":D ", " ").replace(": D.", ".").replace(":D.", ".")
    drunkPostString = drunkPostString.replace("; )", "").replace(";)", "").replace("; ).", ".").replace(";).", ".")
    drunkPostString = drunkPostString.replace("; -)", "").replace(";-)", "").replace("; -).", ".").replace(";-).", ".")

    # add space after symbol
    drunkPostString = re.sub(r"\!(?=[A-ZÕÄÖÜ])", "! ", drunkPostString)  # fix: add space after "!"
    drunkPostString = re.sub(r"\,(?=[a-zA-ZõäöüÕÄÖÜ])", ", ", drunkPostString)  # fix: add space after ","
    drunkPostString = re.sub(r"\.(?=[A-ZÕÄÖÜ])", ". ", drunkPostString)  # fix: add space after "."
    # drunkPostString = re.sub(r"\;(?=[a-zA-ZõäöüÕÄÖÜ])", "; ", drunkPostString)  # fix: add space after ";"
    drunkPostString = re.sub(r"\?(?=[A-ZÕÄÖÜ])", "? ", drunkPostString)  # fix: add space after "?"

    # add space between symbols
    drunkPostString = drunkPostString.replace(",(", ", (")
    drunkPostString = drunkPostString.replace(".(", ". (")
    drunkPostString = drunkPostString.replace(".<", ". <")
    drunkPostString = drunkPostString.replace(":<", ": <")
    drunkPostString = drunkPostString.replace(":\"", ": \"")

    # remove needless dublicates
    drunkPostString = drunkPostString.replace(")))", ")").replace("))", ")")

    # remove odd combinations
    drunkPostString = drunkPostString.replace("!. ", "! ").replace("! .", "!")
    drunkPostString = drunkPostString.replace(",.", ",").replace(", .", ",")
    drunkPostString = drunkPostString.replace("?.", "?").replace("? .", "?")

    # remove space before symbol
    drunkPostString = drunkPostString.replace("  ", " ")
    drunkPostString = drunkPostString.replace(" !", "!")
    drunkPostString = drunkPostString.replace(" ) ", ") ")
    drunkPostString = drunkPostString.replace(" )", ") ")
    drunkPostString = drunkPostString.replace(" ),", "),")
    drunkPostString = drunkPostString.replace(" ).", ").")
    drunkPostString = drunkPostString.replace(" ,", ",")
    drunkPostString = drunkPostString.replace(" ?", "?")
    drunkPostString = drunkPostString.replace(' ".', '".')

    # remove space after symbol
    drunkPostString = drunkPostString.replace("  ", " ")
    drunkPostString = drunkPostString.replace(" ( ", " (").replace("( ", " (")
    drunkPostString = drunkPostString.replace('. " ', '. "')

    # remove space between symbols
    drunkPostString = drunkPostString.replace(") ,", "),")
    drunkPostString = drunkPostString.replace(") .", ").")
    drunkPostString = drunkPostString.replace(". )", ".)")
    drunkPostString = drunkPostString.replace(". </", ".</")
    drunkPostString = drunkPostString.replace(": </", ":</")
    drunkPostString = drunkPostString.replace('" .', '".')
    drunkPostString = drunkPostString.replace('. " ', '." ')

    # oneline combinations
    drunkPostString = drunkPostString.replace(" ... ", "...").replace(" ..", ". ").replace(". .", ". ").replace(" .", ". ")
    drunkPostString = drunkPostString.replace("- ", " - ").replace("- - ", "-- ").replace("-- ", " -- ").replace(" - ", " -- ")  # to change " - " to " -- ", and keep others
    drunkPostString = drunkPostString.replace(".... ", "... ").replace(".. ", ". ").replace(".. ", "... ")  # to remove '.. ', and keep '... '

    return drunkPostString


def float_to_datetime(floatDateTime, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    rss_print.print_debug(__file__, "floatDateTime = '" + str(floatDateTime) + "'", 5)
    rss_print.print_debug(__file__, "rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 5)
    datetimeRFC2822 = utils.formatdate(floatDateTime, True, True)
    rss_print.print_debug(__file__, "datetimeRFC2822 = '" + str(datetimeRFC2822) + "'", 4)

    return datetimeRFC2822


def format_tags(htmlString, searchTagStart, searchTagEnd, addedTagStart, addedTagEnd):
    if (htmlString.find(searchTagStart) < 0):
        rss_print.print_debug(__file__, "ei leidnud searchTagStart = '" + str(searchTagStart) + "', lõpetame", 4)
        return htmlString

    rss_print.print_debug(__file__, "leidsime searchTagStart = '" + str(searchTagStart) + "', tegeleme", 4)

    rss_print.print_debug(__file__, "\n inpHtmlString = \n'" + str(htmlString) + "'\n", 2)

    # splitime lõpu järgi
    inpStringSplittedByEnd = htmlString.split(searchTagEnd)
    countEnds = len(inpStringSplittedByEnd)

    if countEnds == 0:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + ", lõpetame", 0)
        return htmlString
    if countEnds == 1:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + "", 1)
    else:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + "", 4)

    iAlreadyChanged = -1
    for i in range(countEnds - 1):
        rss_print.print_debug(__file__, "[" + str(i) + "] inpStringSplittedByEnd[" + str(i) + "] = \n'" + str(inpStringSplittedByEnd[i]) + "'", 2)

        if (i == iAlreadyChanged):
            rss_print.print_debug(__file__, "[" + str(i) + "] juba muudetud väärtus: inpStringSplittedByEnd[" + str(i) + "] = \n'" + str(inpStringSplittedByEnd[i]) + "', liigume järgmisele", 2)
            continue
        if (inpStringSplittedByEnd[i].find(searchTagStart) < 0):
            rss_print.print_debug(__file__, "[" + str(i) + "] ei leidnud searchTagStart = '" + str(searchTagStart) + "', liigume järgmisele", 4)
            continue
        else:
            rss_print.print_debug(__file__, "[" + str(i) + "] leidsime searchTagStart = '" + str(searchTagStart) + "', tegeleme", 4)

        splitByEndStringSplitByStart = inpStringSplittedByEnd[i].split(searchTagStart)

        countEndStarts = len(splitByEndStringSplitByStart)  # siin esimene ei loe

        if countEndStarts - 1 > 1:
            rss_print.print_debug(__file__, "[" + str(i) + "] algus(" + searchTagStart + ") leide: " + str(countEndStarts - 1) + "", 0)
        elif countEndStarts - 1 == 1:
            rss_print.print_debug(__file__, "[" + str(i) + "] algus(" + searchTagStart + ") leide: " + str(countEndStarts - 1) + "", 3)
        else:
            rss_print.print_debug(__file__, "[" + str(i) + "] algus(" + searchTagStart + ") leide: " + str(countEndStarts - 1) + "", 0)

        # paneme alguse paika
        splitByEndStringSplitByStart[1] = addedTagStart + splitByEndStringSplitByStart[1]

        # genereerime otsinguks lõputägist nn algusttagi
        searchStartTagFromSearchEnd = searchTagEnd.replace("</", "<").replace(">", "") + " "

        for j in range(countEndStarts):
            curNr = "[" + str(i) + "][" + str(j) + "/" + str(countEndStarts - 1) + "]"
            rss_print.print_debug(__file__, curNr + " asume uurima: splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 4)

            if (splitByEndStringSplitByStart[j] == ""):
                continue
            elif (splitByEndStringSplitByStart[j].find(searchStartTagFromSearchEnd) < 0):
                # sisus div-e juurde ei tuld, saame rahus lõpetada
                rss_print.print_debug(__file__, curNr + " ei leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 2)
                splitByEndStringSplitByStart[j] = splitByEndStringSplitByStart[j] + addedTagEnd
                rss_print.print_debug(__file__, curNr + " lõppu lisatud: splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 2)
                break
            elif (j == countEndStarts - 1):
                # sisus tuli div-e juurde, aga oleme lõpus, peame liikuma edasi
                rss_print.print_debug(__file__, curNr + " viimasest leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 2)
                for k in range(i + 1, countEnds - 1):
                    rss_print.print_debug(__file__, curNr + "[" + str(k) + "] liigume sammu edasi", 4)
                    inpStringSplittedByEnd[k] = addedTagEnd + inpStringSplittedByEnd[k]
                    rss_print.print_debug(__file__, curNr + "[" + str(k) + "] muudetud järgmine inpStringSplittedByEnd[" + str(k) + "] = '" + str(inpStringSplittedByEnd[k]) + "'", 2)
                    iAlreadyChanged = k
                    break
            else:
                rss_print.print_debug(__file__, curNr + " leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 0)
                # peame liikuma kindlasti edasi

        # paneme tükid kokku tagasi
        inpStringSplittedByEnd[i] = searchTagStart.join(splitByEndStringSplitByStart)
        rss_print.print_debug(__file__, "[" + str(i) + "] kokkupandud inpStringSplittedByEnd[" + str(i) + "] = '" + str(inpStringSplittedByEnd[i]) + "'", 2)

    htmlString = searchTagEnd.join(inpStringSplittedByEnd)
    rss_print.print_debug(__file__, "\n outHtmlString = \n'" + str(htmlString) + "'\n", 2)

    return htmlString


def get_article_string(session, domainText, articleUrl, noCache):
    """
    Artikli sisu hankimine cachest või internetist
    """

    # kontrollime urli korrektsust
    if (articleUrl.find('http', 0, 4) == -1):
        rss_print.print_debug(__file__, "lingist ei leitud http-d: " + str(articleUrl), 3)
        articleUrl = domain_url(domainText, articleUrl)

    # tegutseme vastavalt poliitikale
    if (rss_config.ARTICLE_CACHE_POLICY == 'all'):
        # hangime alati kettalt, või tagastame tühja sisu
        rss_print.print_debug(__file__, "ei päri kunagi internetist: " + articleUrl, 1)
        htmlPageString = rss_disk.get_url_string_from_cache(articleUrl)
    elif (rss_config.ARTICLE_CACHE_POLICY == 'auto'):
        if noCache is True:
            rss_print.print_debug(__file__, "nocache==" + str(noCache) + ", põhilehekülg tuleb alati alla laadida Internetist: " + articleUrl, 2)
            htmlPageString = rss_makereq.get_url_as_html_string(session, articleUrl)
        else:
            # proovime kõigepealt hankida kettalt
            rss_print.print_debug(__file__, "nocache==" + str(noCache) + ", proovime enne internetipäringut kettalt lugeda: " + articleUrl, 2)
            htmlPageString = rss_disk.get_url_string_from_cache(articleUrl)

            if htmlPageString != "":
                rss_print.print_debug(__file__, "lugesime enne internetipäringut kettalt: " + articleUrl, 1)
            else:
                rss_print.print_debug(__file__, "ei õnnestunud kettalt lugeda, pärime internetist: " + articleUrl, 1)

                # teeme internetipäringu
                htmlPageString = rss_makereq.get_url_as_html_string(session, articleUrl)
    elif (rss_config.ARTICLE_CACHE_POLICY == 'off'):
        # teeme alati internetipäringu
        rss_print.print_debug(__file__, "pärime alati internetist: " + articleUrl, 1)
        htmlPageString = rss_makereq.get_url_as_html_string(session, articleUrl)
    else:
        rss_print.print_debug(__file__, "tundmatu allalaadimise poliitika rss_config.ARTICLE_CACHE_POLICY: " + rss_config.ARTICLE_CACHE_POLICY, 0)

    # fix link addresses
    htmlPageString = htmlPageString.replace('src="//', 'src="http://')
    htmlPageString = htmlPageString.replace('src="./', 'src="' + domainText + '/')
    htmlPageString = htmlPageString.replace('src="/', 'src="' + domainText + '/')
    htmlPageString = htmlPageString.replace('href="//', 'href="http://')
    htmlPageString = htmlPageString.replace('href="./', 'href="' + domainText + '/')
    htmlPageString = htmlPageString.replace('href="/', 'href="' + domainText + '/')

    return htmlPageString


def get_article_tree(session, domainText, articleUrl, noCache):
    # hangib lehe cachest või netist
    htmlPageString = get_article_string(session, domainText, articleUrl, noCache)

    # puhastab lehe üleliigsest jamast
    htmlPageString = html_string_cleanup(htmlPageString)

    # loob edaspidiseks html objekti
    htmlPageTree = html_tree_from_string(htmlPageString, articleUrl)

    return htmlPageTree


def html_string_cleanup(htmlPageString):
    '''
    Puhastame üleliigsest prügist: js, style jne
    '''

    # remove style
    htmlPageString = re.sub(r"<style[\s\S]*?<\/style>", "", htmlPageString)

    # remove scripts
    htmlPageString = re.sub(r"<script[\s\S]*?<\/script>", "", htmlPageString)

    # remove comments
    htmlPageString = re.sub(r"<!--[\s\S]*?-->", "", htmlPageString)

    # remove scripts from links
    htmlPageString = re.sub(r' onclick=(\")[\s\S]*?(\")', "", htmlPageString)

    # eemaldame html-i vahelise whitespace-i
    htmlPageString = re.sub(r"\s\s+(?=<)", "", htmlPageString)

    # remove trackers from links
    htmlPageString = re.sub(r'&_[a-zA-Z0-9_-]*', "", htmlPageString)  # delfi
    htmlPageString = re.sub(r'_ga=[0-9.-]*', "", htmlPageString)
    htmlPageString = re.sub(r'fbclid=[0-9A-Za-z-]*', "", htmlPageString)
    htmlPageString = re.sub(r'gclid=[0-9A-Za-z-_]*', "", htmlPageString)
    htmlPageString = re.sub(r'utm_source=[0-9A-Za-z-.&_=]*', "", htmlPageString)
    htmlPageString = re.sub(r'utm_source=pm_fb[0-9A-Za-z&_=]*', "", htmlPageString)
    htmlPageString = htmlPageString.replace("?&", "?")

    # eemaldame allesjäänud tühikud
    htmlPageString = htmlPageString.replace('\\n', ' ')
    htmlPageString = htmlPageString.replace('\\r', ' ')
    htmlPageString = htmlPageString.replace('\\t', ' ')
    htmlPageString = " ".join(htmlPageString.split())

    # remove useless space
    htmlPageString = htmlPageString.replace("<br/>", "<br>")
    htmlPageString = htmlPageString.replace("<br><br>", "<br>")

    # add newline
    htmlPageString = htmlPageString.replace("<strong>", "<br><strong>")

    # add space
    htmlPageString = htmlPageString.replace("</p>", "</p> ")
    htmlPageString = htmlPageString.replace("</td>", "</td> ")

    return htmlPageString


def html_to_string(htmlNode):
    if isinstance(htmlNode, str):
        rss_print.print_debug(__file__, "sisend on juba string, tagastame sisendi", 0)
        rss_print.print_debug(__file__, "sisend on juba string: htmlNode = " + htmlNode, 3)
        return htmlNode

    stringAsBytes = html.tostring(htmlNode)
    string = str(stringAsBytes)
    return string


def html_tree_from_string(htmlPageString, articleUrl):
    if (htmlPageString == ""):
        rss_print.print_debug(__file__, "puudub html stringi sisu leheküljel: " + articleUrl, 0)
        htmlTree = html.fromstring("<html><head></head></html>")

    try:
        htmlTree = html.document_fromstring(htmlPageString)
    except Exception as e:
        rss_print.print_debug(__file__, "ei õnnestunud luua mitteutf-8 html objekti leheküljest: " + articleUrl, 1)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

        # kui unicode ei käi, proovime utf-8 "Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration."
        htmlPageStringUtf = htmlPageString.encode('utf-8')
        htmlTree = html.document_fromstring(htmlPageStringUtf)

    return htmlTree


def lchop(inpString, stripString):
    if (inpString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: inpString = '" + str(inpString) + "'", 3)
        return inpString
    if (stripString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: stripString = '" + str(stripString) + "'", 0)
        return inpString

    # constant
    stripStringLen = len(stripString)

    while (inpString.find(stripString) == 0):
        inpString = inpString[stripStringLen:]
        rss_print.print_debug(__file__, "eemaldasime algusest stringi: '" + str(stripString) + "'", 4)

    return inpString


def months_to_int(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    # est long
    rawDateTimeText = rawDateTimeText.replace('jaanuar', '01').replace('veebruar', '02').replace('märts', '03').replace('aprill', '04').replace('mai', '05').replace('juuni', '06')
    rawDateTimeText = rawDateTimeText.replace('juuli', '07').replace('august', '08').replace('september', '09').replace('oktoober', '10').replace('november', '11').replace('detsember', '12')
    # est short
    rawDateTimeText = rawDateTimeText.replace('jaan', '01').replace('veebr', '02').replace('veeb', '02').replace('märts', '03').replace('mär', '03')
    rawDateTimeText = rawDateTimeText.replace('aprill', '04').replace('mai', '05').replace('juun', '06')
    rawDateTimeText = rawDateTimeText.replace('juul', '07').replace('aug', '08').replace('sept', '09')
    rawDateTimeText = rawDateTimeText.replace('okt', '10').replace('nov', '11').replace('dets', '12')
    # eng short
    rawDateTimeText = rawDateTimeText.replace('jan', '01').replace('feb', '02').replace('mar', '03').replace('apr', '04').replace('may', '05').replace('jun', '06')
    rawDateTimeText = rawDateTimeText.replace('jul', '07').replace('aug', '08').replace('sep', '09').replace('oct', '10').replace('nov', '11').replace('dec', '12')

    return rawDateTimeText


def raw_to_datetime(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    curDateTimeText = rawDateTimeText
    curDateTimeText = curDateTimeText.strip()
    curDateTimeText = lchop(curDateTimeText, "\\t")
    curDateTimeText = rchop(curDateTimeText, "\\r\\n")

    if (curDateTimeText == ""):
        rss_print.print_debug(__file__, "ajasisend tühi: curDateTimeText = '" + curDateTimeText + "'", 0)
    else:
        rss_print.print_debug(__file__, "curDateTimeText = '" + curDateTimeText + "'", 5)

    if (rawDateTimeSyntax == ""):
        rss_print.print_debug(__file__, "ajasisend tühi: rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 0)
    else:
        rss_print.print_debug(__file__, "rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 5)

    datetimeFloat = raw_to_float(curDateTimeText, rawDateTimeSyntax)
    datetimeRFC2822 = float_to_datetime(datetimeFloat, rawDateTimeSyntax)

    return datetimeRFC2822


def raw_to_float(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist float tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    curDateTimeText = rawDateTimeText.strip()
    if (curDateTimeText == ""):
        rss_print.print_debug(__file__, "ajasisend tühi: curDateTimeText = '" + curDateTimeText + "'", 0)
        return 0

    datetimeStruct = time.strptime(curDateTimeText, rawDateTimeSyntax)
    datetimeList = list(datetimeStruct)

    if datetimeList[0] == 1900:
        if datetimeList[1] > int(time.strftime('%m')):
            rss_print.print_debug(__file__, "muudame puuduva aasta eelmiseks aastaks", 0)
            datetimeList[0] = int(time.strftime('%Y')) - 1
        else:
            rss_print.print_debug(__file__, "muudame puuduva aasta praeguseks aastaks", 0)
            datetimeList[0] = int(time.strftime('%Y'))

    datetimeTuple = tuple(datetimeList)
    datetimeFloat = time.mktime(datetimeTuple)

    return datetimeFloat


def remove_weekday_strings(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    # est
    rawDateTimeText = rawDateTimeText.replace('esmaspäev', "").replace('teisipäev', "").replace('kolmapäev', "")
    rawDateTimeText = rawDateTimeText.replace('neljapäev', "").replace('reede', "").replace('laupäev', "").replace('pühapäev', "")

    return rawDateTimeText


def replace_string_with_timeformat(inpString, stringToReplace, dateTimeformat, offSetDays=0):
    if (inpString.find(stringToReplace) >= 0):
        inpString = inpString.replace(stringToReplace, str((datetime.now() + timedelta(days=offSetDays)).strftime(dateTimeformat)))
        rss_print.print_debug(__file__, "asendasime stringis sõna ajaga: '" + stringToReplace + "' -> " + inpString, 3)

    return inpString


def rchop(inpString, stripString):
    """
    Eemaldab sisendstringi lõpust kõik etteantud stringid
    """

    if (inpString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: inpString = '" + str(inpString) + "'", 3)
        return inpString
    if (stripString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: stripString = '" + str(stripString) + "'", 0)
        return inpString

    # constant
    stripStringLen = len(stripString)

    while (inpString.rfind(stripString) >= 0):
        inpStringLen = len(inpString)
        inpStringLenWithoutStripString = inpStringLen - stripStringLen

        if (inpString.rfind(stripString) == inpStringLenWithoutStripString):
            inpString = inpString[:inpStringLenWithoutStripString]
            rss_print.print_debug(__file__, "eemaldasime lõpust stringi '" + str(stripString) + "': " + str(inpString), 4)
            continue

        #  default is to break after no finds
        break
    return inpString


def simplify_link(inpString):
    inpString = lchop(inpString, "https://")
    inpString = lchop(inpString, "http://")
    inpString = lchop(inpString, "www.")
    return inpString


def stringify_index_children(sourceList, index):
    if (index >= len(sourceList)):
        rss_print.print_debug(__file__, "sisendilistis pole indeksit " + str(index) + ", tagastame tühja sisu", 0)
        return ""

    htmlNode = sourceList[index]
    htmlNodeChilds = stringify_children(htmlNode)

    return htmlNodeChilds


def stringify_children(htmlNode):
    """
    Given a LXML tag,
    Return contents as a string
    >>> html = "<p><strong>Sample sentence</strong> with tags.</p>"
    >>> htmlNode = lxml.html.fragment_fromstring(html)
    >>> extract_html_content(htmlNode)
    "<strong>Sample sentence</strong> with tags."
    From: https://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml/32468202#32468202
    """

    if htmlNode is None:
        rss_print.print_debug(__file__, "pole otsitavat parentit (htmlNode is None), tagastame tühja sisu", 1)
        return ""

    if (len(htmlNode) == 0):
        rss_print.print_debug(__file__, "osakontroll1: (if (len(htmlNode) == 0):)", 4)
        if not getattr(htmlNode, 'text', None):
            rss_print.print_debug(__file__, "osakontroll2: (if not getattr(htmlNode, 'text', None):)", 4)
            rss_print.print_debug(__file__, "pole otsitavat parentit (htmlNode-s puudub attr. 'text'), tagastame tühja sisu", 3)
            return ""
    if isinstance(htmlNode, str):
        rss_print.print_debug(__file__, "stringify_children() sisend on string, ehk juba töödeldud?, katkestame töötluse", 0)
        return htmlNode

    # teeme htmli-st stringi
    retString = html_to_string(htmlNode)

    tagOpening = retString.find(">") + 1
    tagClosing = retString.rfind("<")

    # lõikame stringist vajaliku osa
    retString = retString[tagOpening:tagClosing]

    return retString


def time_float():
    curTimeFloat = time.time()

    return curTimeFloat


def xpath_path_validator(xpathString, parent=False):
    if xpathString.find("/html") != 0 and xpathString.find("//") != 0:
        rss_print.print_debug(__file__, "xpath-i stringi algus mittekorrektne: " + xpathString, 0)
    if xpathString.find('""') >= 0:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '\"\"', asendame '\"'-ga: " + xpathString, 0)
        xpathString = xpathString.replace('""', '"')
    if xpathString.find('["') >= 0:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '[\"', asendame '[@'-ga: " + xpathString, 0)
        xpathString = xpathString.replace('["', "[@")
    if xpathString.find("///") >= 0:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '///', asendame '//'-ga: " + xpathString, 0)
        xpathString = xpathString.replace("///", "//")
    if re.search(r"\[([a-zA-Z])\w+", xpathString):
        rss_print.print_debug(__file__, "xpath-i stringis on kummaline '[*', äkki on '@' puudu: " + xpathString, 0)
    if xpathString.find("  ") > 0:
        rss_print.print_debug(__file__, "xpath-i stringis on '  ', millised programm on lehelt juba eemaldanud, asendame: " + xpathString, 0)
        xpathString = xpathString.replace('   ', ' ')
        xpathString = xpathString.replace('  ', ' ')
    if re.search(r"\[([0-9]*)\]", xpathString):
        rss_print.print_debug(__file__, "xpath-i stringis on '[nr', tasuks vältida: " + xpathString, 3)

    xpathStringEnd = xpathString.split("/")[-1]

    if parent is False:
        logLevelHas = 5
        logLevelNot = 0
    else:
        logLevelHas = 0
        logLevelNot = 5

    if xpathStringEnd.find("text()") == 0:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on 'text()': " + xpathString, logLevelHas)
    elif xpathStringEnd.find("@") == 0:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on '@': " + xpathString, logLevelHas)
    elif xpathStringEnd.find("node()") == 0:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on 'node()': " + xpathString, logLevelHas)
    else:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is puudub ('node()','text()','@'): " + xpathString, logLevelNot)

    return xpathString


def xpath_to_list(pageTree, xpathString, parent=False):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid
    """

    xpathString = xpath_path_validator(xpathString, parent)

    elements = pageTree.xpath(xpathString)

    if (parent is True):
        rss_print.print_debug(__file__, "laseme nimekirja läbi funktsiooni stringify_index_children", 4)
    for i in range(len(elements)):
        # enne hangimine, kui vaja
        if (parent is True):
            elements[i] = stringify_index_children(elements, i)
        # ja siis ühine strip
        elements[i] = elements[i].strip()

    if not elements:
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtuste pikkus: " + str(len(elements)), 0)
    elif len(elements) > 1:
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtuste pikkus: " + str(len(elements)), 4)
    else:
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtuste pikkus: " + str(len(elements)), 1)

    rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtused: elements = " + str(elements), 3)

    return elements


def xpath_to_list_devel(pageTree, xpathString, parent=False):
    rss_print.print_debug(__file__, "xpath-i stringi pärimine funktsiooni 'xpath_to_list_devel' kaudu: " + xpathString, 0)

    xpathString = xpath_path_validator(xpathString, parent)

    while (True):
        elements = pageTree.xpath(xpathString)

        if elements:
            rss_print.print_debug(__file__, "xpath-i " + str(len(elements)) + " stringi leitud: " + xpathString, 0)
            rss_print.print_debug(__file__, "elements: " + str(elements), 3)
            return elements

        rss_print.print_debug(__file__, "xpath-i stringile ei leitud vasteid: " + xpathString, 0)

        if len(xpathString.split("/")) <= 3:
            rss_print.print_debug(__file__, "xpath-i ei anna enam lühendada: " + xpathString, 0)
            return elements

        rss_print.print_debug(__file__, "xpath-i lühendamine algusest: " + xpathString, 0)
        xpathString = "//" + "/".join(xpathString.replace("/html", "//").split("/")[3:])


def xpath_to_single(pageTree, xpathString, parent=False, combine=False):
    """

    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objekt
    """

    xpathString = xpath_path_validator(xpathString, parent)

    element = next(iter(pageTree.xpath(xpathString) or [""]), None)

    if (parent is True):
        element = stringify_children(element)

    if not element:
        rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtuse pikkus: " + str(len(element)), 2)
        element = ""
    elif len(element) > 1:
        rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtuse pikkus: " + str(len(element)), 4)

    rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtuse: '" + str(element) + "'", 3)

    return element
