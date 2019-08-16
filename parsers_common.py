#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Erinevate parserid ja funktsioonid
"""

import hashlib
import time
import lxml
import re
from datetime import datetime
from email import utils
from lxml import html

import rss_makereq
import rss_print


def add_to_time_string(curArtPubDate, curDateFormat):
    curArtPubDate = datetime.now().strftime(curDateFormat) + curArtPubDate
    rss_print.print_debug(__file__, "lisasime tänasele kellaajale kuupäeva: " + curArtPubDate, 3)
    return curArtPubDate


def articleUrlsRange(articleUrls):
    """
    Esimesest edasi kuni objektide lõpuni
    """
    rss_print.print_debug(__file__, 'xpath parsimisel leitud artikleid: ' + str(len(articleUrls)), 2)
    return range(0, len(articleUrls))


def articlePostsRange(articlePosts, maxArticlePostsCount):
    """
    Viimasest tagasi kuni piirarvu täitumiseni
    """
    rss_print.print_debug(__file__, 'xpath parsimisel leitud artikli poste: ' + str(len(articlePosts)), 2)
    return range(max(0, len(articlePosts) - maxArticlePostsCount), len(articlePosts))


def capitalizeFirst(inpString):
    return inpString[0:1].capitalize() + inpString[1:]


def del_article_dict_index(articleDataDict, k):
    rss_print.print_debug(__file__, "eemaldame mittesoovitud kande: '" + articleDataDict["titles"][k] + "'", 1)

    articleDataDict["authors"] = del_if_set(articleDataDict["authors"], k)
    articleDataDict["descriptions"] = del_if_set(articleDataDict["descriptions"], k)
    articleDataDict["images"] = del_if_set(articleDataDict["images"], k)
    articleDataDict["pubDates"] = del_if_set(articleDataDict["pubDates"], k)
    articleDataDict["titles"] = del_if_set(articleDataDict["titles"], k)
    articleDataDict["urls"] = del_if_set(articleDataDict["urls"], k)

    return articleDataDict


def del_if_set(inpList, inpIndex):
    indexHumanreadable = inpIndex + 1
    if len(inpList) >= indexHumanreadable:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(len(inpList)) + ", eemaldasime listi elemendi nr: " + str(indexHumanreadable), 4)
        del inpList[inpIndex]
    else:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(len(inpList)) + ", ei eemaldand listi elementi nr: " + str(indexHumanreadable), 4)
    return inpList


def domainUrl(domain, articleUrl):
    """
    Ühendab domeenid URLidega
    """
    articleUrl = domain.rstrip('/') + '/' + articleUrl.lstrip('./').lstrip('/')
    rss_print.print_debug(__file__, "pärast domeeni lisamist lingile: " + str(articleUrl), 4)
    return articleUrl


def domainUrls(domain, urls):
    """
    Ühendab domeenid URLidega
    """
    domainUrls = []
    for i in range(0, len(urls)):
        domainUrls.append(domainUrl(domain, urls[i]))
    return domainUrls


def elemtreeToString(elemTree):
    return fixStringSpaces(str(lxml.html.tostring(elemTree)))


def fixDrunkPost(drunkPostString):
    drunkPostString = drunkPostString.replace("  ", " ")
    drunkPostString = drunkPostString + " "

    drunkPostString = drunkPostString.replace(" :", ": ")
    drunkPostString = drunkPostString.replace(":<", ": <").replace(": </", ":</")
    drunkPostString = drunkPostString.replace(": -)", " ").replace(":-)", " ")
    drunkPostString = drunkPostString.replace(": -D", " ").replace(":-D", " ")
    drunkPostString = drunkPostString.replace(": ) ", " ").replace(":) ", " ")
    drunkPostString = drunkPostString.replace(": D ", " ").replace(":D ", " ")
    drunkPostString = drunkPostString.replace("; ) ", " ").replace(";) ", " ")

    # fix: space after dot
    drunkPostString = re.sub(r"\.(?=[A-Z])", ". ", drunkPostString)
    drunkPostString = drunkPostString.replace('" .', '".')
    drunkPostString = drunkPostString.replace(" ... ", "...").replace(" ..", ". ").replace(". .", ". ").replace(" .", ". ")
    drunkPostString = drunkPostString.replace(".... ", "... ").replace(".. ", ". ").replace(".. ", "... ")  # to remove '.. ', and keep '... '
    drunkPostString = drunkPostString.replace(".<", ". <").replace(". </", ".</")
    drunkPostString = drunkPostString.replace(".(", ". (")
    drunkPostString = drunkPostString.replace('. "', '."')

    # fix: space after commas
    drunkPostString = re.sub(r"\,(?=[a-zA-Z])", ", ", drunkPostString)
    drunkPostString = drunkPostString.replace(",.", ", ")
    drunkPostString = drunkPostString.replace(",(", ", (")
    drunkPostString = drunkPostString.replace(" ,", ", ")

    drunkPostString = drunkPostString.replace("?. ", "? ")
    drunkPostString = drunkPostString.replace(" ?", "? ")

    drunkPostString = drunkPostString.replace(" !", "! ")

    drunkPostString = drunkPostString.replace(" ( ", " (").replace("( ", " (")
    drunkPostString = drunkPostString.replace(" ) ", ") ").replace(" )", ") ")
    drunkPostString = drunkPostString.replace(" ).", "). ").replace(") . ", "). ")
    drunkPostString = drunkPostString.replace(" ),", "), ").replace(") ,", "), ")

    drunkPostString = drunkPostString.replace("  ", " ")
    return drunkPostString


def fixStringSpaces(inpString):
    """
    Tagastab formaatimata teksti
    Sisend utf-8 kujul inpString
    """

    inpString = inpString.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    inpString = " ".join(inpString.split())
    inpString = inpString.strip()

    return inpString


def format_tags(htmlString, searchTagStart, searchTagEnd, addedTagStart, addedTagEnd):
    if (htmlString.find(searchTagStart) < 0):
        rss_print.print_debug(__file__, "ei leidnud searchTagStart = '" + str(searchTagStart) + "', lõpetame", 4)
        return htmlString
    else:
        rss_print.print_debug(__file__, "leidsime searchTagStart = '" + str(searchTagStart) + "', tegeleme", 4)

    rss_print.print_debug(__file__, "\n inpHtmlString = \n'" + str(htmlString) + "'\n", 1)

    # splitime lõpu järgi
    inpStringSplittedByEnd = htmlString.split(searchTagEnd)
    countEnds = len(inpStringSplittedByEnd)

    if countEnds == 0:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + ", lõpetame", 0)
        return htmlString
    elif countEnds == 1:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + "", 1)
    else:
        rss_print.print_debug(__file__, "lõpu(" + searchTagEnd + ") leide: " + str(countEnds) + "", 4)

    iAlreadyChanged = -1
    for i in range(0, countEnds - 1):
        rss_print.print_debug(__file__, "[" + str(i) + "] inpStringSplittedByEnd[" + str(i) + "] = \n'" + str(inpStringSplittedByEnd[i]) + "'", 1)

        if (i == iAlreadyChanged):
            rss_print.print_debug(__file__, "[" + str(i) + "] juba muudetud väärtus: inpStringSplittedByEnd[" + str(i) + "] = \n'" + str(inpStringSplittedByEnd[i]) + "', liigume järgmisele", 1)
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
            rss_print.print_debug(__file__, "[" + str(i) + "] algus(" + searchTagStart + ") leide: " + str(countEndStarts - 1) + "", 1)
        else:
            rss_print.print_debug(__file__, "[" + str(i) + "] algus(" + searchTagStart + ") leide: " + str(countEndStarts - 1) + "", 0)

        # paneme alguse paika
        splitByEndStringSplitByStart[1] = addedTagStart + splitByEndStringSplitByStart[1]

        # genereerime otsinguks lõputägist nn algusttagi
        searchStartTagFromSearchEnd = searchTagEnd.replace("</", "<").replace(">", "") + " "

        for j in range(0, countEndStarts):
            curNr = "[" + str(i) + "][" + str(j) + "/" + str(countEndStarts - 1) + "]"
            rss_print.print_debug(__file__, curNr + " asume uurima: splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 4)

            if (splitByEndStringSplitByStart[j] == ""):
                continue
            elif (splitByEndStringSplitByStart[j].find(searchStartTagFromSearchEnd) < 0):
                # sisus div-e juurde ei tuld, saame rahus lõpetada
                rss_print.print_debug(__file__, curNr + " ei leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 1)
                splitByEndStringSplitByStart[j] = splitByEndStringSplitByStart[j] + addedTagEnd
                rss_print.print_debug(__file__, curNr + " lõppu lisatud: splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 1)
                break
            elif (j == countEndStarts - 1):
                # sisus tuli div-e juurde, aga oleme lõpus, peame liikuma edasi
                rss_print.print_debug(__file__, curNr + " viimasest leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 1)
                for k in range(i + 1, countEnds - 1):
                    rss_print.print_debug(__file__, curNr + "[" + str(k) + "] liigume sammu edasi", 1)
                    inpStringSplittedByEnd[k] = addedTagEnd + inpStringSplittedByEnd[k]
                    rss_print.print_debug(__file__, curNr + "[" + str(k) + "] muudetud järgmine inpStringSplittedByEnd[" + str(k) + "] = '" + str(inpStringSplittedByEnd[k]) + "'", 1)
                    iAlreadyChanged = k
                    break
            else:
                rss_print.print_debug(__file__, curNr + " leitud algustäg(" + searchStartTagFromSearchEnd + "): splitByEndStringSplitByStart[" + str(j) + "] = '" + str(splitByEndStringSplitByStart[j]) + "'", 0)
                # peame liikuma kindlasti edasi

        # paneme tükid kokku tagasi
        inpStringSplittedByEnd[i] = searchTagStart.join(splitByEndStringSplitByStart)
        rss_print.print_debug(__file__, "[" + str(i) + "] kokkupandud inpStringSplittedByEnd[" + str(i) + "] = '" + str(inpStringSplittedByEnd[i]) + "'", 1)

    htmlString = searchTagEnd.join(inpStringSplittedByEnd)
    rss_print.print_debug(__file__, "\n outHtmlString = \n'" + str(htmlString) + "'\n", 1)
    return htmlString


def getArticleData(domain, articleUrl, mainPage=False):
    if (articleUrl.find('http', 0, 4) == -1):
        rss_print.print_debug(__file__, "lingist ei leitud http-d: " + str(articleUrl), 3)
        articleUrl = domainUrl(domain, articleUrl)
    return rss_makereq.getArticleData(articleUrl, mainPage)


def htmlToString(htmlNode, pageTreeEcoding='utf-8'):
    if (type(htmlNode) is str):
        rss_print.print_debug(__file__, "sisend on juba string: htmlNode = " + str(htmlNode), 2)
        return htmlNode
    else:
        rss_print.print_debug(__file__, "type(htmlNode) = " + str(type(htmlNode)), 2)
        rss_print.print_debug(__file__, "htmlNode = " + str(htmlNode), 2)
        stringAsBytes = html.tostring(htmlNode, encoding=pageTreeEcoding)
        string = str(stringAsBytes)
    return string


def lstrip_string(inpString, stripString):
    if (inpString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: inpString = '" + str(inpString) + "'", 3)
        return inpString
    if (stripString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: stripString = '" + str(stripString) + "'", 0)
        return inpString
    lenStripString = len(stripString)
    while (inpString.find(stripString) == 0):
        rss_print.print_debug(__file__, "eemaldasime algusest stringi: '" + str(stripString) + "'", 4)
        inpString = inpString[lenStripString:]
    return inpString


def rstrip_string(inpString, stripString):
    if (inpString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: inpString = '" + str(inpString) + "'", 3)
        return inpString
    if (stripString == ""):
        rss_print.print_debug(__file__, "sisend tühi, katkestame: stripString = '" + str(stripString) + "'", 0)
        return inpString
    lenStripString = len(stripString)
    while (inpString.find(stripString) == len(inpString) - lenStripString):
        rss_print.print_debug(__file__, "eemaldasime lõpust stringi '" + str(stripString) + "': " + str(inpString), 4)
        inpString = inpString[:len(inpString) - lenStripString]
    return inpString


def maxArticleCount(articleUrl):
    """
    Hashi genereerimine lehekülje URList
    """
    return hashlib.md5(articleUrl.encode('utf-8')).hexdigest()


def floatToDatetime(floatDateTime, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    rss_print.print_debug(__file__, "floatDateTime = '" + str(floatDateTime) + "'", 3)
    rss_print.print_debug(__file__, "rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 4)
    datetime_RFC2822 = utils.formatdate(floatDateTime, True, True)
    rss_print.print_debug(__file__, "datetime_RFC2822 = '" + str(datetime_RFC2822) + "'", 4)
    return datetime_RFC2822


def rawToDatetime(rawDateTimeText, rawDateTimeSyntax):
    """
    Teeb sissentud ajatekstist ja süntaksist datetime tüüpi aja
    rawDateTimeText = aeg teksti kujul, näiteks: "23. 11 2007 /"
    rawDateTimeSyntax = selle teksti süntaks, näiteks "%d. %m %Y /"
    Süntaksi seletus: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    rss_print.print_debug(__file__, "rawDateTimeText = '" + rawDateTimeText + "'", 3)
    rss_print.print_debug(__file__, "rawDateTimeSyntax = '" + rawDateTimeSyntax + "'", 4)
    datetime_float = rawToFloat(rawDateTimeText, rawDateTimeSyntax)
    datetime_RFC2822 = floatToDatetime(datetime_float, rawDateTimeSyntax)
    return datetime_RFC2822


def rawToFloat(rawDateTimeText, rawDateTimeSyntax):
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
    datetime_struct = time.strptime(curDateTimeText, rawDateTimeSyntax)
    rss_print.print_debug(__file__, "datetime_struct = " + str(datetime_struct), 4)
    datetime_list = list(datetime_struct)

    if datetime_list[0] == 1900:
        if datetime_list[1] > int(time.strftime('%m')):
            rss_print.print_debug(__file__, "muudame puuduva aasta eelmiseks aastaks", 0)
            datetime_list[0] = int(time.strftime('%Y')) - 1
        else:
            rss_print.print_debug(__file__, "muudame puuduva aasta praeguseks aastaks", 0)
            datetime_list[0] = int(time.strftime('%Y'))

    datetime_tuple = tuple(datetime_list)
    datetime_float = time.mktime(datetime_tuple)
    rss_print.print_debug(__file__, "datetime_float = '" + str(datetime_float) + "'", 4)
    return datetime_float


def removeWeekDayTexts(rawDateTimeText):
    rawDateTimeText = rawDateTimeText.replace('  ', ' ').strip().lower()
    # est
    rawDateTimeText = rawDateTimeText.replace('esmaspäev', "").replace('teisipäev', "").replace('kolmapäev', "")
    rawDateTimeText = rawDateTimeText.replace('neljapäev', "").replace('reede', "").replace('laupäev', "").replace('pühapäev', "")
    return rawDateTimeText


def monthsToNumber(rawDateTimeText):
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


def stringify_index_children(sourceList, index, pageTreeEcoding='utf-8'):
    if (index >= len(sourceList)):

        rss_print.print_debug(__file__, "sisendilistis pole indeksit " + str(index) + ", tagastame tühja sisu", 0)
        return ""

    node = sourceList[index]
    nodeChilds = stringify_children(node, pageTreeEcoding='utf-8')
    return nodeChilds


def stringify_children(node, pageTreeEcoding='utf-8'):
    """
    Given a LXML tag, return contents as a string
    >>> html = "<p><strong>Sample sentence</strong> with tags.</p>"
    >>> node = lxml.html.fragment_fromstring(html)
    >>> extract_html_content(node)
    "<strong>Sample sentence</strong> with tags."
    From: https://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml/32468202#32468202
    """
    if node is None or (len(node) == 0 and not getattr(node, 'text', None)):
        rss_print.print_debug(__file__, "pole otsitavat parentit, tagastame tühja sisu", 2)
        return ""
    node.attrib.clear()
    opening_tag = len(node.tag) + 2
    closing_tag = -(len(node.tag) + 4)
    ret = html.tostring(node, encoding=pageTreeEcoding)[opening_tag:closing_tag]
    try:
        ret = ret.decode(pageTreeEcoding)
    except Exception:
        rss_print.print_debug(__file__, "parandame ebaõnnestunud 'UTF-8' kodeeringu")
        ret = rss_makereq.fixBrokenUTF8asEncoding(ret, 'iso8859_15')
        ret = ret.decode(pageTreeEcoding)
    ret = toPlaintext(ret)
    return ret


def toPlaintext(rawText):
    """
    Tagastab formaatimata teksti
    Sisend utf-8 kujul rawText
    """

    rawText = rawText.replace('<strong>', '<br><strong>').replace('</td>', '</td> ').replace('</p>', '</p> ')

    retString = fixStringSpaces(rawText)
    return retString


def urlToHash(articleUrl):
    """
    Hashi genereerimine lehekülje URList
    """

    return hashlib.md5(articleUrl.encode('utf-8')).hexdigest()


def xpath_helper(xpathString, exact=True):
    if xpathString.find('""') > 0:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '\"\"', asendame '\"'-ga: " + xpathString, 0)
        xpathString = xpathString.replace('""', '"')
    if xpathString.find("///") > 0:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '///', asendame '//'-ga: " + xpathString, 0)
        xpathString = xpathString.replace("///", "//")
    if xpathString.find("//") > 0 and xpathString.find("/html") != 0:
        rss_print.print_debug(__file__, "xpath-i stringi algus mittekorrektne: " + xpathString, 0)
    if xpathString.find("/tbody") > 0:
        rss_print.print_debug(__file__, "xpath-i stringi sees on '/tbody', see ei pruugi töötada: " + xpathString, 1)
    if xpathString[1:].find("//") > 0:
        rss_print.print_debug(__file__, "xpath-i stringi sees on '//', tasuks optimeerida: " + xpathString, 1)

    if exact is True:
        xpathStringEnd = xpathString.split("/")[-1]
        if xpathStringEnd.find("node()") < 0 and xpathStringEnd.find("text()") < 0 and xpathStringEnd.find("@") < 0:
            rss_print.print_debug(__file__, "xpath-i stringis pole otsingut('node()','text()','@'): " + xpathString, 2)

    return xpathString


def xpath_parent_to_single(pageTree, xpathString):
    curParent = xpath_to_single(pageTree, xpathString)  # as a parent

    curChilds = stringify_children(curParent)
    rss_print.print_debug(__file__, "curChilds: " + str(curChilds), 3)
    return curChilds


def xpath_to_list(pageTree, xpathString):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid
    """

    xpathString = xpath_helper(xpathString, False)

    elements = pageTree.xpath(xpathString)

    rss_print.print_debug(__file__, "tagastame xpathi: '" + xpathString + "' väärtused: elements = " + str(elements), 3)
    return elements


def xpath_to_list_devel(pageTree, xpathString):
    rss_print.print_debug(__file__, "xpath-i stringi pärimine funktsiooni 'xpath_to_list_devel' kaudu: " + xpathString, 0)

    xpathString = xpath_helper(xpathString, False)

    while(True):
        elements = pageTree.xpath(xpathString)
        if len(elements) > 0:
            rss_print.print_debug(__file__, "xpath-i " + str(len(elements)) + " stringi leitud: " + xpathString, 0)
            rss_print.print_debug(__file__, "elements: " + str(elements), 2)
            return elements
        else:
            rss_print.print_debug(__file__, "xpath-i stringile ei leitud vasteid: " + xpathString, 0)
            if len(xpathString.split("/")) < 3:
                rss_print.print_debug(__file__, "xpath-i ei anna lühendada: " + xpathString, 0)
                return elements
            else:
                rss_print.print_debug(__file__, "xpath-i lühendamine algusest: " + xpathString, 0)
                xpathString = "//" + "/".join(xpathString.replace("/html", "//").split("/")[3:])


def xpath_to_single(pageTree, xpathString):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objekt
    """

    xpathString = xpath_helper(xpathString, True)

    element = next(iter(pageTree.xpath(xpathString) or [""]), None)

    rss_print.print_debug(__file__, "tagastame xpathi: '" + xpathString + "' väärtuse: element = " + str(element), 3)
    return element
