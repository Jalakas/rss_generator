#!/usr/bin/env python3

"""
    Erinevate parserid ja funktsioonid
"""

from html import unescape
from lxml import html  # sudo apt install python3-lxml
import re

import rss_config
import rss_disk
import rss_makereq
import rss_print
import rss_stat


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
        rss_print.print_debug(__file__, "vaikimisi '" + inpEncoding + "' dekodeerimine EBAõnnestus, proovime vigade ignoreerimisega", 0)
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

    rss_print.print_debug(__file__, "parandame EBAõnnestunud kodeeringu asendamise läbi", 1)
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

    rss_print.print_debug(__file__, "EBAõnnestunud '" + sourceEncoding + "' as '" + destEncoding + "' kodeeringu parandamine 'tagasiasendamisega'", 1)
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


def fix_quatation_tags(inpString, oldTagStart, oldTagEnd, newTagStart, newTagEnd):
    if oldTagStart not in inpString:
        rss_print.print_debug(__file__, "ei leidnud oldTagStart = '" + oldTagStart + "', lõpetame", 4)
        return inpString
    rss_print.print_debug(__file__, "leidsime oldTagStart = '" + oldTagStart + "', tegeleme", 3)

    # algus                                                     # <div class="quotecontent">
    oldTagStartNice = oldTagStart.split("<")[1].split(">")[0]   # div class="quotecontent"
    oldTagStartList = oldTagStartNice.split(" ")                # div, class="quotecontent"
    oldTagStartList1 = oldTagStartList[1].split("=")            # class, "quotecontent"
    oldTagStartList1[1] = oldTagStartList1[1].strip('"')        # quotecontent

    newTagStartNice = newTagStart.split("<")[1].split(">")[0]

    pageTree = html_tree_from_string(inpString, "")
    elements = pageTree.iter(oldTagStartList[0])

    for el in elements:
        rss_print.print_debug(__file__, "fix_quatation_tags: '" + oldTagStart + "' kontrollime elementi: " + str(el.tag), 4)
        elAttributes = el.attrib

        if elAttributes:
            rss_print.print_debug(__file__, "fix_quatation_tags: '" + oldTagStart + "' kontrollime elemendi attribuuti: " + str(elAttributes), 4)
            rss_print.print_debug(__file__, "fix_quatation_tags: '" + oldTagStart + "' kontrollime elemendi attribuuti: " + str(oldTagStartList1[0]) + " ?= " + str(oldTagStartList1[1]), 4)

            if elAttributes[oldTagStartList1[0]] == oldTagStartList1[1]:
                rss_print.print_debug(__file__, "fix_quatation_tags: '" + oldTagStart + "' leidsime elemendi attribuudi: " + str(elAttributes), 3)
                el.tag = newTagStartNice
                rss_print.print_debug(__file__, "fix_quatation_tags: '" + oldTagStart + "' muudetud tag: <" + str(el.tag) + ">", 2)

    inpString = html_to_string(pageTree, prettyPrint=False)

    # remove html and body elements
    inpString = html_string_children(inpString)
    inpString = html_string_children(inpString)

    return inpString


def get_article_tree(session, curDomainShort, curDomainLong, noCache):

    # kontrollime url-i korrektsust
    if curDomainLong.find('http', 0, 4) != 0:
        rss_print.print_debug(__file__, "lingist ei leitud http-d: " + str(curDomainLong), 1)
        curDomainLong = domain_url(curDomainShort, curDomainLong)

    # tegutseme vastavalt poliitikale - artikli sisu hankimine cachest või internetist
    if (rss_config.ARTICLE_CACHE_POLICY == 'all'):
        # hangime alati kettalt, või tagastame tühja sisu
        rss_print.print_debug(__file__, "ei päri internetist: " + curDomainLong, 2)
        htmlPageString = rss_disk.get_url_string_from_cache(curDomainLong)
    elif (rss_config.ARTICLE_CACHE_POLICY == 'auto'):
        if noCache is True:
            rss_print.print_debug(__file__, "nocache==" + str(noCache) + ", põhilehekülg tuleb alati alla laadida Internetist: " + curDomainLong, 3)
            htmlPageString = rss_makereq.get_url_string_from_internet(session, curDomainShort, curDomainLong)
        else:
            # proovime kõigepealt hankida kettalt
            rss_print.print_debug(__file__, "nocache==" + str(noCache) + ", proovime enne internetipäringut kettalt lugeda: " + curDomainLong, 3)
            htmlPageString = rss_disk.get_url_string_from_cache(curDomainLong)

            if htmlPageString != "":
                rss_print.print_debug(__file__, "lugesime enne internetipäringut kettalt: " + curDomainLong, 3)
            else:
                # teeme internetipäringu
                rss_print.print_debug(__file__, "ei õnnestunud kettalt lugeda, pärime internetist: " + curDomainLong, 1)
                htmlPageString = rss_makereq.get_url_string_from_internet(session, curDomainShort, curDomainLong)
    elif (rss_config.ARTICLE_CACHE_POLICY == 'off'):
        # teeme alati internetipäringu
        rss_print.print_debug(__file__, "pärime alati internetist: " + curDomainLong, 1)
        htmlPageString = rss_makereq.get_url_string_from_internet(session, curDomainShort, curDomainLong)
    else:
        rss_print.print_debug(__file__, "tundmatu allalaadimise poliitika rss_config.ARTICLE_CACHE_POLICY: " + rss_config.ARTICLE_CACHE_POLICY, 0)

    # puhastame lehe üleliigsest jamast
    htmlPageString = html_page_cleanup(htmlPageString)

    # fix link addresses
    htmlPageString = htmlPageString.replace('src="//', 'src="http://')
    htmlPageString = htmlPageString.replace('src="./', 'src="' + curDomainShort + '/')
    htmlPageString = htmlPageString.replace('src="/', 'src="' + curDomainShort + '/')
    htmlPageString = htmlPageString.replace('href="//', 'href="http://')
    htmlPageString = htmlPageString.replace('href="./', 'href="' + curDomainShort + '/')
    htmlPageString = htmlPageString.replace('href="/', 'href="' + curDomainShort + '/')
    rss_print.print_debug(__file__, "html string: " + htmlPageString, 5)

    # loob edaspidiseks html objekti
    htmlPageTree = html_tree_from_string(htmlPageString, curDomainLong)

    return htmlPageTree


def html_page_cleanup(htmlPageString):
    '''
    Puhastame üleliigsest prügist: js, style jne
    '''

    # remove styles
    htmlPageString = re.sub(r"<style[\s\S]*?<\/style>", "", htmlPageString)

    # remove scripts
    htmlPageString = re.sub(r"<script[\s\S]*?<\/script>", "", htmlPageString)

    # remove comments
    htmlPageString = re.sub(r"<!--[\s\S]*?-->", "", htmlPageString)

    # remove scripts from links
    htmlPageString = re.sub(r' onclick=(\")[\s\S]*?(\")', "", htmlPageString)
    htmlPageString = re.sub(r" onclick=(')[\s\S]*?(')", "", htmlPageString)

    # remove trackers from links
    htmlPageString = re.sub(r'(&|\?)_[0-9A-Za-z_-]*', "", htmlPageString)  # delfi
    htmlPageString = re.sub(r'_ga=[0-9.-]*', "", htmlPageString)
    htmlPageString = re.sub(r'fbclid=[0-9A-Za-z-]*', "", htmlPageString)
    htmlPageString = re.sub(r'gclid=[0-9A-Za-z-_]*', "", htmlPageString)
    htmlPageString = re.sub(r'utm_source=[0-9A-Za-z-.&_=]*', "", htmlPageString)
    htmlPageString = re.sub(r'utm_source=pm_fb[0-9A-Za-z&_=]*', "", htmlPageString)
    htmlPageString = htmlPageString.replace("?&", "?")

    # eemaldame html-i vahelise whitespace-i
    htmlPageString = re.sub(r"\s\s+(?=<)", "", htmlPageString)

    # eemaldame allesjäänud tühikud
    htmlPageString = htmlPageString.replace('\\n', ' ')
    htmlPageString = htmlPageString.replace('\\r', ' ')
    htmlPageString = htmlPageString.replace('\\t', ' ')
    htmlPageString = " ".join(htmlPageString.split())

    # remove useless space
    htmlPageString = htmlPageString.replace("<br/>", "<br>")
    htmlPageString = htmlPageString.replace(" <br>", "<br>")
    htmlPageString = htmlPageString.replace("<br><br>", "<br>")

    return htmlPageString


def html_post_cleanup(htmlPostString):

    # remove attributes
    htmlPostString = re.sub(r' alt=(\")[\s\S]*?(\")', "", htmlPostString)
    htmlPostString = re.sub(r' class=(\")[\s\S]*?(\")', "", htmlPostString)
    htmlPostString = re.sub(r' id=(\")[\s\S]*?(\")', "", htmlPostString)
    htmlPostString = re.sub(r' rel=(\")[\s\S]*?(\")', "", htmlPostString)
    htmlPostString = re.sub(r' style=(\")[\s\S]*?(\")', "", htmlPostString)
    htmlPostString = re.sub(r' target=(\")[\s\S]*?(\")', "", htmlPostString)
    htmlPostString = re.sub(r' zoompage-fontsize=(\")[\s\S]*?(\")', "", htmlPostString)

    # remove elements
    htmlPostString = htmlPostString.replace("<hr>", "")
    htmlPostString = re.sub(r'<span[\s\S]*?>', "", htmlPostString)
    htmlPostString = htmlPostString.replace("</span>", "")

    # change elements
    htmlPostString = htmlPostString.replace("<strong>", "<b>")
    htmlPostString = htmlPostString.replace("</strong>", "</b>")
    htmlPostString = htmlPostString.replace("<blockquote><br>", "<blockquote>")
    htmlPostString = htmlPostString.replace("</blockquote><br>", "</blockquote>")
    htmlPostString = htmlPostString.replace("<td ", "<p ")
    htmlPostString = htmlPostString.replace("</td>", "</p>")

    # br
    htmlPostString = htmlPostString.replace(" <br>", "<br>")
    htmlPostString = htmlPostString.replace("<br><br>", "<br>")

    # div
    htmlPostString = htmlPostString.replace("<div></div>", "")

    # i
    htmlPostString = htmlPostString.replace("<i></i>", "")

    # p
    htmlPostString = htmlPostString.replace("<p></p>", "")
    htmlPostString = htmlPostString.replace("<p> ", "<p>")
    htmlPostString = htmlPostString.replace(" </p>", "</p>")

    return htmlPostString


def html_string_children(htmlString):

    if not isinstance(htmlString, str):
        rss_print.print_debug(__file__, "html_string_children() sisend pole string, tagastame tühjuse", 0)
        return ""

    if "</" not in htmlString:
        rss_print.print_debug(__file__, "html_string_children() sisendis pole child elementi, tagastame sisendi", 0)
        return htmlString

    tagOpening = htmlString.find(">") + 1
    tagClosing = htmlString.rfind("<")

    # lõikame stringist vajaliku osa
    htmlString = htmlString[tagOpening:tagClosing]

    return htmlString


def html_to_string(htmlNode, prettyPrint=False):

    if isinstance(htmlNode, str):
        rss_print.print_debug(__file__, "sisend on juba string, tagastame sisendi", 0)
        rss_print.print_debug(__file__, "sisend on juba string: htmlNode = " + htmlNode, 3)
        return htmlNode

    htmlStringAsBytes = html.tostring(htmlNode, encoding="unicode", pretty_print=prettyPrint)

    htmlString = str(htmlStringAsBytes)
    htmlString = unescape(htmlString)
    rss_print.print_debug(__file__, "htmlString = " + htmlString, 4)

    return htmlString


def html_tree_from_string(htmlPageString, articleUrl):

    rss_print.print_debug(__file__, "asume looma html objekti: " + articleUrl, 3)

    if (htmlPageString == ""):
        rss_print.print_debug(__file__, "puudub html stringi sisu leheküljel: " + articleUrl, 0)
        htmlTree = html.fromstring("<html><head></head></html>")
        return htmlTree

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

    while (inpString.startswith(stripString)):
        inpString = inpString.removeprefix(stripString)

    return inpString


def remove_weekday_strings(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    # est
    rawDateTimeText = rawDateTimeText.replace('esmaspäev', "").replace('teisipäev', "").replace('kolmapäev', "")
    rawDateTimeText = rawDateTimeText.replace('neljapäev', "").replace('reede', "").replace('laupäev', "").replace('pühapäev', "")

    return rawDateTimeText


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

    while (inpString.endswith(stripString)):
        inpString = inpString.removesuffix(stripString)

    return inpString


def simplify_link(inpString):
    inpString = lchop(inpString, "https://")
    inpString = lchop(inpString, "http://")
    inpString = lchop(inpString, "www.")
    return inpString


def title_at_domain(articleTitle, domain):
    curTitle = rchop(articleTitle, ".")
    curTitle += " @"
    curTitle += simplify_link(domain)

    return curTitle


def xpath_debug(pageTree):
    htmlTreeString = html_to_string(pageTree, prettyPrint=True)
    htmlTreeString = htmlTreeString.split("<body ")[1]
    htmlTreeString = htmlTreeString.split("</body>")[0]
    htmlTreeString = "<body " + htmlTreeString + "</body>"
    rss_disk.write_file(rss_config.PATH_FILENAME_DEBUG, htmlTreeString)


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

    if xpathStringEnd.startswith("text()"):
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on 'text()': " + xpathString, logLevelHas)
    elif xpathStringEnd.startswith("@"):
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on '@': " + xpathString, logLevelHas)
    elif xpathStringEnd.startswith("node()"):
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is on 'node()': " + xpathString, logLevelHas)
    else:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is puudub ('node()','text()','@'): " + xpathString, logLevelNot)

    return xpathString


def xpath_to_list(pageTree, xpathString, parent=False, count=False):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid
    """

    if pageTree is None:
        rss_print.print_debug(__file__, "pageTree puudub, katkestame", 0)

    xpathString = xpath_path_validator(xpathString, parent)

    # get data
    elements = pageTree.xpath(xpathString)
    elementsLen = len(elements)

    if elementsLen == 0:
        rss_stat.save_path(count, xpathString, found=False)
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' leide: " + str(elementsLen), 1)
    elif elementsLen == 1:
        rss_stat.save_path(count, xpathString, found=True)
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' leide: " + str(elementsLen), 3)
    else:
        rss_stat.save_path(count, xpathString, found=True)
        rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' leide: " + str(elementsLen), 3)

    for i in range(len(elements)):

        if (i >= len(elements)):
            rss_print.print_debug(__file__, "sisendilistis pole indeksit " + str(i) + ", tagastame tühja sisu", 0)
            return ""

        elem = elements[i]

        if elem is None:
            rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtus[" + str(i) + "] is None, tagastame tühja sisu", 0)
            elements[i] = ""
        elif not isinstance(elem, str):
            rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtus[" + str(i) + "] pole string: " + str(elem), 3)
            # teeme tekstiks
            elem = html_to_string(elem, prettyPrint=False)
            rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtus[" + str(i) + "] stringimise järel: " + elem, 4)

        if "</" in elem:
            if parent is True:
                # eemaldame ülemelemendi vaikselt
                rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtus[" + str(i) + "] on hoitatud parent: " + elem, 3)
                elem = html_string_children(elem)
            else:
                # eemaldame ülemelemendi lärmakalt
                rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtus[" + str(i) + "] on hoiatamata parent?: " + elem, 0)
                elem = html_string_children(elem)
        else:
            if parent is True:
                # eemaldame ülemelemendi vaikselt
                rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtus[" + str(i) + "] on valestimääratud parent?: " + elem, 0)

        # ja siis ühine strip
        elements[i] = elem.strip()

    rss_print.print_debug(__file__, "xpath_to_list: '" + xpathString + "' väärtused: elements = " + str(elements), 4)

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


def xpath_to_single(pageTree, xpathString, parent=False, count=False, multi=False):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objekt
    """

    if pageTree is None:
        rss_print.print_debug(__file__, "pageTree puudub, katkestame", 0)
        return ""

    xpathString = xpath_path_validator(xpathString, parent)

    # get data
    elements = pageTree.xpath(xpathString)
    elementsLen = len(elements)

    if elementsLen == 0:
        rss_stat.save_path(count, xpathString, found=False)
        rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' leide: " + str(elementsLen), 2)
    elif elementsLen == 1:
        rss_stat.save_path(count, xpathString, found=True)
        rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' leide: " + str(elementsLen), 3)
    else:
        rss_stat.save_path(count, xpathString, found=True)
        if multi is False:
            rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' oodati ühte, leide: " + str(elementsLen), 0)
            elementsLen = 1
        else:
            rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' leide: " + str(elementsLen), 3)

    element = ""
    for i in range(elementsLen):
        elem = elements[i]

        if elem is None:
            rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtus[" + str(i) + "] is None, tagastame tühja sisu", 0)
            elem = ""
        if not isinstance(elem, str):
            rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtus[" + str(i) + "] pole string: " + str(elem), 3)
            # teeme tekstiks
            elem = html_to_string(elem, prettyPrint=False)
            rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtus[" + str(i) + "] stringimise järel: " + elem, 4)

        if "</" in elem:
            if parent is True:
                # eemaldame ülemelemendi vaikselt
                rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtus[" + str(i) + "] on hoitatud parent: " + elem, 3)
                elem = html_string_children(elem)
            else:
                # eemaldame ülemelemendi lärmakalt
                rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtus[" + str(i) + "] on hoiatamata parent?: " + elem, 0)
                elem = html_string_children(elem)
        else:
            if parent is True:
                # eemaldame ülemelemendi vaikselt
                rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väärtus[" + str(i) + "] on valestimääratud parent?: " + elem, 0)

        element = element + elem

    rss_print.print_debug(__file__, "xpath_to_single: '" + xpathString + "' väljund: '" + element + "'", 4)

    return element
