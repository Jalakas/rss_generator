
"""
    Erinevate parserid ja funktsioonid.
"""

import re

import lxml

import parsers_html
import rss_config
import rss_disk
import rss_makereq
import rss_print
import rss_stat


def article_data_dict_clean(fileName, articleDataDict, inpFilters, inpCond, dictField):
    """
    Eemaldame tingimusele vastavad kanded.
    """
    if not articleDataDict[dictField]:
        rss_print.print_debug(__file__, "tühi sisend: articleDataDict", 1)
        return articleDataDict

    if not inpFilters:
        rss_print.print_debug(__file__, "tühi sisend: inpFilters", 0)
        return articleDataDict

    # muudame kõik filtri tekstid väiketähtedeks
    sortedFilters = []
    for inpFilter in inpFilters:
        sortedFilters.append(inpFilter.casefold())

    # kui eemaldamise tingimuseks on filtri tekstis sisaldumine, siis eelistame lühemaid filtreid eespool
    if inpCond == "in":
        sortedFilters.sort(key=len)
    # kui eemaldamise tingimuseks on filtri tekstiga kokkulangemine, siis eelistame pikemaid filtreid eespool, saame kedratavaid liste varem väiksemaks
    # kui eemaldamise tingimuseks on filtri tekstist puudumine, siis eelistame pikemaid filtreid eespool
    elif (inpCond == "==") or (inpCond == "not in"):
        sortedFilters.sort(key=len, reverse=True)

    if len(inpFilters) != len(set(sortedFilters)):
        rss_print.print_debug(__file__, "inpFilters sisaldab duplikaate", 0)
        for sortedFilter in sortedFilters:
            rss_print.print_debug(__file__, "sortedFilter: " + sortedFilter, 0)

    i = 0
    foundLast = False
    found = False
    lastSortedFilter = ''
    lastArticleDataDictElem = ''
    while i < len(articleDataDict[dictField]):
        articleDataDictElem = articleDataDict[dictField][i]
        articleDataDictElem = articleDataDictElem.casefold()

        # kontrollime eemaldamistingimusele vastamist
        if lastArticleDataDictElem and lastArticleDataDictElem == articleDataDictElem:
            foundLast = True
        else:
            for sortedFilter in sortedFilters:
                if inpCond == "in" and sortedFilter in articleDataDictElem:
                    found = True
                    break
                if inpCond == "==" and sortedFilter == articleDataDictElem:
                    found = True
                    break
                if inpCond == "not in" and sortedFilter not in articleDataDictElem:
                    found = True
                    break

        if foundLast is True:
            rss_print.print_debug(__file__, "(" + str(i + 1) + "/" + str(len(articleDataDict[dictField])) + ") kanne sama mis eelmine filtreeritud: '" + lastSortedFilter + "' " + inpCond + " '" + articleDataDictElem + "'", 2)
            articleDataDict = dict_del_article_index(articleDataDict, i)
            rss_stat.save_string_stat(rss_config.PATH_FILENAME_FILTER, True, fileName + ".'" + sortedFilter + "' " + inpCond, True)
            foundLast = False
        elif found is True:
            rss_print.print_debug(__file__, "(" + str(i + 1) + "/" + str(len(articleDataDict[dictField])) + ") kande filtreerimistingimus täidetud: '" + sortedFilter + "' " + inpCond + " '" + articleDataDictElem + "'", 2)
            articleDataDict = dict_del_article_index(articleDataDict, i)
            rss_stat.save_string_stat(rss_config.PATH_FILENAME_FILTER, True, fileName + ".'" + sortedFilter + "' " + inpCond, True)
            found = False
            lastSortedFilter = sortedFilter
            lastArticleDataDictElem = articleDataDictElem
        else:
            i += 1
            rss_stat.save_string_stat(rss_config.PATH_FILENAME_FILTER, True, fileName + ".'" + sortedFilter + "' " + inpCond, False)

    return articleDataDict


def article_posts_range(articlePosts, maxArticlePosts):
    """
    Viimasest tagasi kuni piirarvu täitumiseni.
    """
    articlePostsLen = len(articlePosts)
    rss_print.print_debug(__file__, "xpath parsimisel leitud artikli poste: " + str(articlePostsLen), 2)
    retRange = range(max(0, articlePostsLen - maxArticlePosts), articlePostsLen)

    return retRange


def article_urls_range(articleUrls):
    """
    Esimesest edasi kuni objektide lõpuni.
    """
    articleUrlsLen = len(articleUrls)
    if not articleUrlsLen:
        retRange = range(0)
        rss_print.print_debug(__file__, "xpath parsimisel leitud artikleid: " + str(articleUrlsLen), 1)
    else:
        retRange = range(articleUrlsLen)
        rss_print.print_debug(__file__, "xpath parsimisel leitud artikleid: " + str(articleUrlsLen), 3)

    return retRange


def bytes_to_str(inpBytes, inpEncoding):
    if isinstance(inpBytes, str):
        rss_print.print_debug(__file__, "sisend on juba string, tagastame sisendi", 0)
        return inpBytes

    try:
        if inpEncoding:
            retString = inpBytes.decode(inpEncoding)
        else:
            rss_print.print_debug(__file__, "sisendis puudub kodeering, proovime dekodeerida ilma", 0)
            retString = inpBytes.decode()
    except Exception as e:
        rss_print.print_debug(__file__, "vaikimisi '" + inpEncoding + "' dekodeerimine EBAõnnestus, proovime vigade ignoreerimisega", 1)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        retString = inpBytes.decode(inpEncoding, "replace")

    return retString


def dict_add_dict(articleDataDictMain, articleDataDictNew):
    rss_print.print_debug(__file__, "ühendame dictCur ja dictNew", 4)

    for key in articleDataDictMain.keys():
        articleDataDictMain[key] = articleDataDictMain[key] + articleDataDictNew[key]

    return articleDataDictMain


def dict_del_article_index(articleDataDict, k):
    for key in articleDataDict.keys():
        articleDataDict[key] = list_del_elem_if_set(articleDataDict[key], k)

    return articleDataDict


def dict_reverse_order(articleDataDict):
    """
    Newest events last for feedly ordering.
    """
    maxLen = -1
    for key in articleDataDict.keys():
        curLen = len(articleDataDict[key])
        if curLen > 0:
            if maxLen == -1:
                maxLen = curLen
            elif maxLen != curLen:
                rss_print.print_debug(__file__, "mittekonsistentse pikkusega dict, loobume pööramisest", 0)
                dict_stats(articleDataDict)
                return articleDataDict

    rss_print.print_debug(__file__, "pöörame suuna", 2)

    for key in articleDataDict.keys():
        articleDataDict[key].reverse()

    return articleDataDict


def dict_stats(articleDataDict):
    prevKey = None
    for i, curKey in enumerate(articleDataDict.keys()):
        if i > 0:
            prevKeyCount = len(articleDataDict[prevKey])
        else:
            prevKeyCount = 0
        curKeyCount = len(articleDataDict[curKey])

        if prevKeyCount and curKeyCount and prevKeyCount != curKeyCount:
            rss_print.print_debug(__file__, "'" + curKey + "' väärtuste arv: " + str(curKeyCount) + "!=" + str(prevKeyCount), 0)
            for j in range(max(prevKeyCount, curKeyCount)):
                rss_print.print_debug(__file__, curKey + "[" + str(j) + "]:\t" + str(get(articleDataDict[curKey], j))[:200], 0)
                rss_print.print_debug(__file__, prevKey + "[" + str(j) + "]:\t" + str(get(articleDataDict[prevKey], j))[:200], 0)
        elif curKey == "urls" and not curKeyCount:
            rss_print.print_debug(__file__, "'" + curKey + "' väärtuste arv: " + str(curKeyCount), 0)
        elif curKey == "urls":
            rss_print.print_debug(__file__, "'" + curKey + "' väärtuste arv: " + str(curKeyCount), 1)
        else:
            rss_print.print_debug(__file__, "'" + curKey + "' väärtuste arv: " + str(curKeyCount), 2)

        # prindime sisu, kui tellitakse
        if curKey == "descriptions":
            rss_print.print_debug(__file__, "'" + curKey + "' = " + str(articleDataDict[curKey]), 4)
        else:
            rss_print.print_debug(__file__, "'" + curKey + "' = " + str(articleDataDict[curKey]), 3)

        prevKey = curKey


def fix_quatation_tags(curString, oldTagStart, oldTagEnd, newTagStart, newTagEnd):
    if oldTagStart not in curString:
        rss_print.print_debug(__file__, "ei leidnud oldTagStart = '" + oldTagStart + "', lõpetame", 4)
        return curString
    rss_print.print_debug(__file__, "leidsime oldTagStart = '" + oldTagStart + "', tegeleme", 3)

    # algus                                                      <div class="quotetitle">
    oldTagStartNice = oldTagStart.split("<")[1]                 # div class="quotetitle">
    oldTagStartNice = oldTagStart.split(">")[0]                 # div class="quotetitle"
    oldTagStartList = oldTagStartNice.split(" ")                # div, class="quotetitle"
    oldTagStartList[0] = oldTagStartList[0].strip('<')
    oldTagStartList1 = oldTagStartList[1].split("=")            # class, "quotetitle"
    oldTagStartList1[1] = oldTagStartList1[1].strip('"')        # quotetitle

    newTagStartNice = newTagStart.split("<")[1].split(">")[0]
    rss_print.print_debug(__file__, "oldTagStartList[0] = " + oldTagStartList[0], 4)

    pageTree = parsers_html.html_tree_from_document_string(curString, "fix_quatation_tags")
    elementStrings = pageTree.iter(oldTagStartList[0])

    for elem in elementStrings:
        rss_print.print_debug(__file__, "'" + oldTagStart + "' kontrollime elementi: " + str(elem.tag), 4)
        elAttributes = elem.attrib

        if elAttributes:
            rss_print.print_debug(__file__, "'" + oldTagStart + "' kontrollime elemendi attribuuti: " + str(elAttributes), 4)
            rss_print.print_debug(__file__, "'" + oldTagStart + "' kontrollime elemendi attribuuti: " + str(oldTagStartList1[0]) + " ?= " + str(oldTagStartList1[1]), 4)

            if elAttributes[oldTagStartList1[0]] == oldTagStartList1[1]:
                rss_print.print_debug(__file__, "'" + oldTagStart + "' leidsime elemendi attribuudi: " + str(elAttributes), 3)
                elem.tag = newTagStartNice
                rss_print.print_debug(__file__, "'" + oldTagStart + "' muudetud tag: <" + str(elem.tag) + ">", 3)

    curString = parsers_html.html_to_string(pageTree, prettyPrint=False)

    # remove html and body elements
    curString = parsers_html.html_string_children(curString)

    return curString


def get_variable_name(variable):
    """
        Get Variable Name as String by comparing its ID to globals() Variables' IDs.
        args:
            variable(var): Variable to find name for (Obviously this variable has to exist)

        kwargs:
            globalVariables(dict): Copy of the globals() dict (Adding to Kwargs allows this function to work properly when imported from another .py)
    """
    globalVariables = globals().copy()
    for globalVariable in globalVariables:
        if id(variable) == id(globalVariables[globalVariable]):  # If our Variable's ID matches this Global Variable's ID...
            return globalVariable  # Return its name from the Globals() dict


def get(array, index, printWarning=1):
    try:
        return array[index]
    except Exception as e:
        if printWarning == 1:
            if not array:
                rss_print.print_debug(__file__, "puudub sisend: array=" + str(get_variable_name(array)), 0)
                return ""
            if not index:
                rss_print.print_debug(__file__, "puudub sisend: index ", 0)
                return ""

            rss_print.print_debug(__file__, "array-l '" + str(get_variable_name(array)) + "' puudub index=" + str(index), 0)
            rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

    return ""


def get_article_tree(curDomainShort, curString, cache, pageStamp=""):
    """
    Hangib html puu.
    @cache: cacheOff, cacheStamped, cacheAll
    """
    # kontrollime url-i korrektsust
    if not curString.startswith('http'):
        rss_print.print_debug(__file__, "lingist ei leitud http-d: " + str(curString), 2)
        curString = str_domain_url(curDomainShort, curString)

    # tegutseme vastavalt poliitikale - artikli sisu hankimine cachest või internetist
    if rss_config.CACHE_POLICY_ARTICLE == 'all':
        # hangime alati kettalt, või tagastame tühja sisu
        rss_print.print_debug(__file__, "ainult kettalt hangitav leht: " + curString, 2)
        htmlPageString = rss_disk.get_url_string_from_disk(curString)
    elif rss_config.CACHE_POLICY_ARTICLE == 'auto':
        if cache == 'cacheOff':
            rss_print.print_debug(__file__, "cache==" + str(cache) + ", lehekülg tuleb alati alla laadida Internetist: " + curString, 3)
            htmlPageString = rss_makereq.get_url_from_internet(curString, pageStamp)
        elif cache == 'cacheStamped':
            if pageStamp:
                # proovime kõigepealt hankida kettalt
                rss_print.print_debug(__file__, "cache==" + str(cache) + ", proovime enne internetipäringut kettalt lugeda: " + curString + "#" + pageStamp, 3)
                htmlPageString = rss_disk.get_url_string_from_disk(curString + "#" + pageStamp)
            else:
                rss_print.print_debug(__file__, "cache==" + str(cache) + ", aga puudub pageStamp: '" + pageStamp + "'", 1)
                htmlPageString = ""

            if not htmlPageString:
                # teeme internetipäringu
                rss_print.print_debug(__file__, "ei õnnestunud kettalt lugeda, pärime internetist: " + curString, 1)
                htmlPageString = rss_makereq.get_url_from_internet(curString, pageStamp)
        elif cache == 'cacheAll':
            # proovime kõigepealt hankida kettalt
            rss_print.print_debug(__file__, "cache==" + str(cache) + ", proovime enne internetipäringut kettalt lugeda: " + curString, 3)
            htmlPageString = rss_disk.get_url_string_from_disk(curString)

            if not htmlPageString:
                # teeme internetipäringu
                rss_print.print_debug(__file__, "ei õnnestunud kettalt lugeda, pärime internetist: " + curString, 1)
                htmlPageString = rss_makereq.get_url_from_internet(curString, pageStamp)
        else:
            rss_print.print_debug(__file__, "cache==" + str(cache) + ", tundmatu allalaadimise poliitika!", 0)
    elif rss_config.CACHE_POLICY_ARTICLE == 'off':
        # teeme alati internetipäringu
        rss_print.print_debug(__file__, "pärime alati internetist: " + curString, 1)
        htmlPageString = rss_makereq.get_url_from_internet(curString, pageStamp)
    else:
        rss_print.print_debug(__file__, "tundmatu allalaadimise poliitika rss_config.CACHE_POLICY_ARTICLE: " + rss_config.CACHE_POLICY_ARTICLE, 0)

    # fix short urls
    htmlPageString = parsers_html.html_change_short_urls(htmlPageString, curDomainShort)

    # loob edaspidiseks html objekti
    htmlPageTree = parsers_html.html_tree_from_document_string(htmlPageString, curString)

    return htmlPageTree


def link_add_end(curArtUrl, curArtUrlEnd):
    if not curArtUrl:
        rss_print.print_debug(__file__, "link tühi: " + curArtUrl, 0)
        return curArtUrl
    if not curArtUrlEnd:
        rss_print.print_debug(__file__, "lingi lõpp tühi: " + curArtUrlEnd, 0)
        return curArtUrl

    if "&sid=" in curArtUrl:
        curArtUrl = curArtUrl.split("&sid=")[0]
        rss_print.print_debug(__file__, "lingis üleliigne '&sid': " + curArtUrl, 2)
    if "#" in curArtUrl:
        rss_print.print_debug(__file__, "lingi lõpp on korras: " + curArtUrl, 4)
    elif "#" in curArtUrlEnd:
        curArtUrlEnd = "#" + curArtUrlEnd.split("#")[1]
        rss_print.print_debug(__file__, "lingi lõppu lisati puuduv: " + curArtUrlEnd, 1)
        curArtUrl = curArtUrl + curArtUrlEnd
    else:
        rss_print.print_debug(__file__, "lingi lõpp pole kasutatav: " + curArtUrlEnd, 0)

    return curArtUrl


def list_add(inpList, index, inpData):
    inpList.append(inpData)

    return inpList


def list_add_or_assign(inpList, index, inpData):
    if len(inpList) >= index + 1:
        inpList[index] = inpData
    else:
        inpList.append(inpData)

    return inpList


def list_del_elem_if_set(inpList, inpIndex):
    inpListLen = len(inpList)
    indexHumanreadable = inpIndex + 1
    if inpListLen >= indexHumanreadable:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(inpListLen) + ", eemaldasime listi elemendi nr: " + str(indexHumanreadable), 4)
        del inpList[inpIndex]
    else:
        rss_print.print_debug(__file__, "listi pikkus on: " + str(inpListLen) + ", ei eemaldand listi elementi nr: " + str(indexHumanreadable), 4)

    return inpList


def should_get_article_body(i, curArticleBodies=-1):
    if rss_config.REQUEST_ARTICLE_BODIES is not True:
        rss_print.print_debug(__file__, "artikli kehade hankimine keelatud: " + str(i + 1), 0)
        return False
    if curArticleBodies != -1:
        if i < curArticleBodies:
            return True
        rss_print.print_debug(__file__, "artikli kehade hankimise limiit täis: " + str(i + 1) + "/" + str(curArticleBodies), 4)
        return False
    if i < rss_config.REQUEST_ARTICLE_BODIES_MAX:
        return True

    rss_print.print_debug(__file__, "artikli kehade hankimise limiit täis: " + str(i + 1) + "/" + str(rss_config.REQUEST_ARTICLE_BODIES_MAX), 0)
    return False


def split_failsafe(curString, splitString, index):
    if splitString in curString:
        curString = curString.split(splitString)[index]
    return curString


def str_capitalize_first(curString):
    curString = curString[0:1].capitalize() + curString[1:]

    return curString


def str_cleanup_description(curString):

    curString = str_cleanup_title(curString)

    curString = curString + "."

    curString = curString.replace("?quot;", '"')

    # remove needless dublicates
    while "))" in curString:
        curString = curString.replace("))", ")")
    while ",," in curString:
        curString = curString.replace(",,", ",")
    while "  " in curString:
        curString = curString.replace("  ", " ")

    # remove emoticons
    curString = curString.replace(" :", ": ").replace(":  ", ": ")
    curString = curString.replace(": (", "").replace(":(", "").replace(": (.", ".").replace(":(.", ".")
    curString = curString.replace(": )", "").replace(":)", "").replace(": ).", ".").replace(":).", ".")
    curString = curString.replace(": -(", "").replace(":-(", "").replace(": -(.", ".").replace(":-(.", ".")
    curString = curString.replace(": -)", "").replace(":-)", "").replace(": -).", ".").replace(":-).", ".")
    curString = curString.replace(": -D", "").replace(":-D", "").replace(": -D.", ".").replace(":-D.", ".")
    curString = curString.replace(": D ", " ").replace(":D ", " ").replace(": D.", ".").replace(":D.", ".")
    curString = curString.replace("; )", "").replace(";)", "").replace("; ).", ".").replace(";).", ".")
    curString = curString.replace("; -)", "").replace(";-)", "").replace("; -).", ".").replace(";-).", ".")

    # replace
    curString = curString.replace(" natsi ", " natsionaalsotsialismi ")
    curString = curString.replace(" orki", " tibla")
    curString = curString.replace(" õlud", " õlut")
    curString = curString.replace("Orki", "tibla")
    curString = curString.replace("aksitu", "aksineeritu")
    curString = curString.replace("axer", "akser")
    curString = curString.replace("axi", "aktsi")
    curString = curString.replace("axxi", "aktsi")
    curString = curString.replace("axz", "akts")
    curString = curString.replace("inflatsiooni", "hinnatõusu")
    curString = curString.replace("mordor", "venemaa")
    curString = curString.replace("mordori", "venemaa")
    curString = curString.replace("natsid", "natsionaalsotsialistid")
    curString = curString.replace("natsis", "natsionaalsotsialis")
    curString = curString.replace("ohepöör", "ahapöör")
    curString = curString.replace("utovabad", "juvabad")

    # add space after symbol
    curString = re.sub(r"\!(?=[A-ZÕÄÖÜ])", "! ", curString)  # fix: add space after "!"
    curString = re.sub(r"\.(?=[A-ZÕÄÖÜ])", ". ", curString)  # fix: add space after "."
    curString = re.sub(r"\?(?=[A-ZÕÄÖÜ])", "? ", curString)  # fix: add space after "?"

    # add space between symbols
    curString = curString.replace(",(", ", (")
    curString = curString.replace(".(", ". (")
    curString = curString.replace(".<", ". <")
    curString = curString.replace(":<", ": <")
    curString = curString.replace(":\"", ": \"")

    # remove space before symbol
    curString = curString.replace(" !", "!")
    curString = curString.replace(" ) ", ") ")
    curString = curString.replace(" )", ") ")
    curString = curString.replace(" ),", "),")
    curString = curString.replace(" ).", ").")
    curString = curString.replace(" ;", ";")
    curString = curString.replace(" ?", "?")
    curString = curString.replace(' ".', '".')

    # remove space after symbol
    curString = curString.replace("  ", " ")
    curString = curString.replace(" ( ", " (").replace("( ", " (")
    curString = curString.replace('. " ', '. "')
    curString = re.sub(r"(?<![a-zõäöü])\, (?=[0-9])", ",", curString)  # fix: remove space after "," if number

    # remove space between symbols
    curString = curString.replace(") ,", "),")
    curString = curString.replace(") .", ").")
    curString = curString.replace(". )", ".)")
    curString = curString.replace(". </", ".</")
    curString = curString.replace(": </", ":</")
    curString = curString.replace('" .', '".')
    curString = curString.replace('. " ', '." ')

    # remove odd combinations
    curString = curString.replace("!. ", "! ").replace("! .", "!")
    curString = curString.replace(",.", ",").replace(", .", ",")
    curString = curString.replace("?.", "?").replace("? .", "?")

    # oneline combinations
    curString = curString.replace(" ... ", "...").replace(" ..", ". ").replace(". .", ". ").replace(" .", ". ")
    curString = curString.replace("- ", " - ").replace("- - ", "-- ").replace("-- ", " -- ").replace(" - ", " -- ")  # to change " - " to " -- ", and keep others
    curString = curString.replace(".... ", "... ").replace(".. ", ". ").replace(".. ", "... ")  # to remove '.. ', and keep '... '

    return curString


def str_cleanup_post(curString):
    # remove attributes
    curString = re.sub(r' alt=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' aria-[\s\S]*?=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' border=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' cellpadding=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' cellspacing=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' class=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' clear=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' content=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' data-[\s\S]*?=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' data-[\s\S]*?=(\')[\s\S]*?(\')', "", curString)
    curString = re.sub(r' dir=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' draggable=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' id=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' itemprop=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' itemscope', "", curString)
    curString = re.sub(r' itemtype=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' lang=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' loading=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' rel=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' role=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' srcset=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' style=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' style=(\')[\s\S]*(\')', "", curString)
    curString = re.sub(r' tabindex=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' target=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' width=(\")[\s\S]*?(\")', "", curString)
    curString = re.sub(r' zoompage-fontsize=(\")[\s\S]*?(\")', "", curString)

    # remove elements
    curString = curString.replace("</circle>", "")
    curString = curString.replace("</path>", "")
    curString = curString.replace("</span>", "")
    curString = curString.replace("</svg>", "")
    curString = re.sub(r'<circle[\s\S]*?>', "", curString)
    curString = re.sub(r'<path[\s\S]*?>', "", curString)
    curString = re.sub(r'<span[\s\S]*?>', "", curString)
    curString = re.sub(r'<svg[\s\S]*?>', "", curString)

    # br
    curString = curString.replace("\r\n", "<br>")
    curString = curString.replace("\n", "<br>")
    curString = curString.replace(" <br>", "<br>")
    curString = curString.replace("<br/>", "<br>")
    curString = curString.replace("<br> ", "<br>")

    # change elements
    curString = curString.replace("</blockquote><br>", "</blockquote>")
    curString = curString.replace("</cite>", "</p>")
    curString = curString.replace("</strong>", "</b>")
    curString = curString.replace("</td>", "</p>")
    curString = curString.replace("<blockquote><br>", "<blockquote>")
    curString = curString.replace("<br><blockquote>", "<blockquote>")
    curString = curString.replace("<cite>", "<p>")
    curString = curString.replace("<strong>", "<b>")
    curString = curString.replace("<td ", "<p ")

    # remove elements
    curString = curString.replace("<hr>", "")
    curString = curString.replace("<meta>", "")

    # remove empty pairs
    while "<div></div>" in curString:
        curString = curString.replace("<div></div>", "")
    while "</div><div>" in curString:
        curString = curString.replace("</div><div>", "<br>")
    curString = curString.replace("<g></g>", "")
    curString = curString.replace("<i></i>", "")

    # div
    curString = curString.replace("<br><div>", "<div>")

    # p
    curString = curString.replace(" </p>", "</p>")
    curString = curString.replace("</p> ", "</p>")
    curString = curString.replace("<p> ", "<p>")
    curString = curString.replace("<p></p>", "")
    curString = curString.replace("<p><br>", "<p>")

    while "<br><br>" in curString:
        curString = curString.replace("<br><br>", "<br>")

    return curString


def str_cleanup_title(curString):
    curString = curString.strip()
    curString = str_lchop(curString, "<br>")
    curString = str_rchop(curString, "<br>")
    curString = curString.replace("  ", " ")
    curString = curString.replace(" ,", ",")
    curString = curString.replace("/ ", "/")
    curString = re.sub(r"\,(?=[a-zA-ZõäöüÕÄÖÜ])", ", ", curString)  # fix: add space after ","
    curString = str_capitalize_first(curString)

    return curString


def str_domain_url(domain, articleUrl):
    """
    Ühendab domeeni URLiga.
    """
    articleUrl = domain.rstrip('/') + '/' + articleUrl.lstrip('./').lstrip('/')
    rss_print.print_debug(__file__, "pärast domeeni lisamist lingile: " + str(articleUrl), 4)

    return articleUrl


def str_fix_url_begginning(curString):
    curString = curString.replace("//", "/")
    curString = curString.replace("https:/", "https://")
    curString = curString.replace("http:/", "http://")

    return curString


def str_lchop(curString, stripString):
    if not curString:
        rss_print.print_debug(__file__, "sisend tühi, katkestame: curString = '" + str(curString) + "'", 3)
        return curString
    if not stripString:
        rss_print.print_debug(__file__, "sisend tühi, katkestame: stripString = '" + str(stripString) + "'", 0)
        return curString

    stripStringLen = len(stripString)

    if stripStringLen == 1:
        curString = curString.lstrip(stripString)
    else:
        while curString.startswith(stripString):
            curString = curString[stripStringLen:]

    return curString


def str_lchop_url(curString):
    curString = str_lchop(curString, "https://")
    curString = str_lchop(curString, "http://")
    curString = str_lchop(curString, "mobile.")
    curString = str_lchop(curString, "www.")
    curString = str_lchop(curString, "m.")

    return curString


def str_rchop(curString, stripString):
    """
    Eemaldab sisendstringi lõpust kõik etteantud stringid.
    """
    if not curString:
        rss_print.print_debug(__file__, "sisend tühi, katkestame: curString = '" + str(curString) + "'", 3)
        return curString
    if not stripString:
        rss_print.print_debug(__file__, "sisend tühi, katkestame: stripString = '" + str(stripString) + "'", 0)
        return curString

    stripStringLen = len(stripString)

    if stripStringLen == 1:
        curString = curString.rstrip(stripString)
    else:
        while curString.endswith(stripString):
            curStringLenWithoutStripString = len(curString) - stripStringLen
            curString = curString[:curStringLenWithoutStripString]

    return curString


def str_remove_clickbait(curString):
    curString = re.sub(r"^[0-9A-ZŽŠÕÜÄÖ!?\-– |,„]+[|:!?]+[ ]", "", curString)

    return curString


def str_title_at_domain(articleTitle, domain):
    if not articleTitle:
        rss_print.print_debug(__file__, "sisend tühi: articleTitle = " + articleTitle, 0)
    else:
        articleTitle = articleTitle.rstrip(".")
        articleTitle += " "
    articleTitle += "@"
    articleTitle += str_lchop_url(domain)

    return articleTitle


def xpath_debug(pageTree, xpathString, cutFrom="right"):
    rss_print.print_debug(__file__, "'" + xpathString + "' debug kontrollide algus", 4)

    xpathString = xpathString.replace("/html", "//")

    while True:
        rss_print.print_debug(__file__, "'" + xpathString + "' osakontrolli algus", 4)

        xpathString = str_rchop(xpathString, "/")
        elementStrings = pageTree.xpath(xpathString)

        if not elementStrings:
            rss_print.print_debug(__file__, "'" + xpathString + "' stringile ei leitud vasteid", 3)
        else:
            rss_print.print_debug(__file__, "'" + xpathString + "' stringe leitud: " + str(len(elementStrings)), 0)

        xpathStringSplitted = xpathString.split("/")
        if len(xpathStringSplitted) <= 3:
            rss_print.print_debug(__file__, "'" + xpathString + "' ei anna enam lühendada", 2)
            rss_print.print_debug(__file__, "pageTree=" + parsers_html.html_to_string(pageTree)[:10000], 3)
            break

        if cutFrom == "left":
            if not elementStrings:
                break
            rss_print.print_debug(__file__, "'" + xpathString + "' proovime lühendada vasakult", 4)
            xpathStringSplitted = xpathStringSplitted[3:]
        elif cutFrom == "right":
            if elementStrings:
                break
            rss_print.print_debug(__file__, "'" + xpathString + "' proovime lühendada paremalt", 4)
            xpathStringSplitted = xpathStringSplitted[2:-1]

        xpathString = "//" + "/".join(xpathStringSplitted)  # alates kolmandast, sest kuju on järgmine: //maha/alles


def xpath_path_validator(xpathString, parent, multi):
    if not xpathString.startswith("/html") and not xpathString.startswith("//") and not xpathString.startswith("(//"):
        rss_print.print_debug(__file__, "xpath-i stringi algus mittekorrektne: " + xpathString, 0)
    if '""' in xpathString:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '\"\"', asendame '\"'-ga: " + xpathString, 0)
        xpathString = xpathString.replace('""', '"')
    if '["' in xpathString:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '[\"', asendame '[@'-ga: " + xpathString, 0)
        xpathString = xpathString.replace('["', "[@")
    if "///" in xpathString:
        rss_print.print_debug(__file__, "xpath-i stringis on vigane '///', asendame '//'-ga: " + xpathString, 0)
        xpathString = xpathString.replace("///", "//")
    if not xpathString.find("[last()") and re.search(r"\[([a-zA-Z])\w+", xpathString):
        rss_print.print_debug(__file__, "xpath-i stringis on kummaline '[*', äkki on '@' puudu: " + xpathString, 0)
    if xpathString.find("  ") > 0:
        rss_print.print_debug(__file__, "xpath-i stringis on '  ', millised programm on lehelt juba eemaldanud, asendame: " + xpathString, 0)
        xpathString = xpathString.replace('   ', ' ')
        xpathString = xpathString.replace('  ', ' ')
    if parent is True and xpathString.endswith("/"):
        rss_print.print_debug(__file__, "parent tüüpi xpath-i üleliigne lõpu '/', eemaldame: " + xpathString, 0)
        xpathString = str_rchop(xpathString, "/")
    if re.search(r"\[([0-9]*)\]", xpathString):
        rss_print.print_debug(__file__, "xpath-i stringis on '[nr', tasuks vältida: " + xpathString, 4)

    xpathStringEnd = xpathString.split("/")[-1]

    if not parent:
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
    elif multi is not True:
        rss_print.print_debug(__file__, "parent=" + str(int(parent)) + " xpath-is puudub ('node()','text()','@'): " + xpathString, logLevelNot)

    rss_print.print_debug(__file__, "kontroll tagastab xpath-i: " + xpathString, 4)

    return xpathString


def xpath_to(to, pageTree, xpathString, parent=False, count=False, multi=False):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid.
    @to:
    @pageTree:
    @xpathString:
    @parent:
    @count:
    @multi:
    """
    # pageTree validation
    if pageTree is None:
        rss_print.print_debug(__file__, "'" + xpathString + "' pageTree puudub, katkestame", 0)
        return ""
    if not isinstance(pageTree, lxml.html.HtmlElement):
        rss_print.print_debug(__file__, "'" + xpathString + "' pageTree pole html objekt, katkestame", 0)
        return ""

    # xpathString validation
    xpathString = xpath_path_validator(xpathString, parent, multi)

    # get data
    elementStrings = pageTree.xpath(xpathString)

    elementsLen = len(elementStrings)
    if not elementsLen:
        rss_stat.save_string_stat(rss_config.PATH_FILENAME_STAT, count, xpathString, found=False)
        rss_print.print_debug(__file__, "'" + xpathString + "' leide: " + str(elementsLen), 2)
        # debugime pathi?
        if rss_config.PRINT_MESSAGE_LEVEL >= 2:
            xpath_debug(pageTree, xpathString, "right")
    elif elementsLen == 1:
        rss_stat.save_string_stat(rss_config.PATH_FILENAME_STAT, count, xpathString, found=True)
        rss_print.print_debug(__file__, "'" + xpathString + "' leide: " + str(elementsLen), 3)
    elif elementsLen > 1:
        rss_stat.save_string_stat(rss_config.PATH_FILENAME_STAT, count, xpathString, found=True)
        if to == 'single' and not multi:
            rss_print.print_debug(__file__, "'" + xpathString + "' oodati ühte, leide: " + str(elementsLen), 0)
            elementsLen = 1
        else:
            rss_print.print_debug(__file__, "'" + xpathString + "' leide: " + str(elementsLen), 3)

    if to == 'list':
        return xpath_to_list(elementStrings, elementsLen, xpathString, parent)

    return xpath_to_single(elementStrings, elementsLen, xpathString, parent)


def xpath_to_list(elementStrings, elementsLen, xpathString, parent):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid.
    """
    for i, elem in enumerate(elementStrings):
        if not isinstance(elem, str):
            elem = parsers_html.html_to_string(elem, prettyPrint=False)
            rss_print.print_debug(__file__, "'" + xpathString + "' väärtus[" + str(i) + "] polnud string, stringimise järel: " + elem, 4)

        countParentNodes = parsers_html.html_string_count_parent_nodes(elem, "xpath_to_list")

        if not countParentNodes:
            if parent is True:
                rss_print.print_debug(__file__, "'" + xpathString + "' väärtus[" + str(i) + "] on valestimääratud parent?: " + elem, 0)
        elif countParentNodes == 1:
            elem = parsers_html.html_remove_single_parents(elem)
        elif countParentNodes > 1:
            if parent is True:
                rss_print.print_debug(__file__, "'" + xpathString + "' väärtus[" + str(i) + "] on valestimääratud parent? " + elem, 0)
            else:
                rss_print.print_debug(__file__, "'" + xpathString + "' väärtus[" + str(i) + "] on hoiatatud parent: " + elem, 3)

        # ja siis ühine strip
        elementStrings[i] = elem.strip()

    rss_print.print_debug(__file__, "'" + xpathString + "' väärtused: elementStrings = " + str(elementStrings), 4)

    return elementStrings


def xpath_to_single(elementStrings, elementsLen, xpathString, parent):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objekt.
    """
    element = ""

    # peab olema nii, kuna mitteoodatud mitmese leiu korral pandaks muidu väärtused kokku
    for i in range(elementsLen):
        elem = elementStrings[i]

        if not isinstance(elem, str):
            elem = parsers_html.html_to_string(elem, prettyPrint=False)
            rss_print.print_debug(__file__, "'" + xpathString + "' väärtus[" + str(i) + "] polnud string, stringimise järel: " + elem, 4)

        countParentNodes = parsers_html.html_string_count_parent_nodes(elem, "xpath_to_single")

        if not countParentNodes:
            if parent is True:
                rss_print.print_debug(__file__, "'" + xpathString + "' väärtus[" + str(i) + "] on valestimääratud parent?: " + elem, 0)
        elif countParentNodes == 1:
            elem = parsers_html.html_remove_single_parents(elem)
        elif countParentNodes > 1:
            if parent is True:
                rss_print.print_debug(__file__, "'" + xpathString + "' väärtus[" + str(i) + "] on valestimääratud parent? " + elem, 0)
            else:
                rss_print.print_debug(__file__, "'" + xpathString + "' väärtus[" + str(i) + "] on hoiatatud parent: " + elem, 3)

        elem = elem.strip()
        if elem:
            if element:
                element += "<br>"
            element += elem

    rss_print.print_debug(__file__, "'" + xpathString + "' väljund: '" + element + "'", 4)

    return element
