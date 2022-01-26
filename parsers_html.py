
"""
    Erinevate parserid ja funktsioonid.
"""

import re
from html import unescape

from lxml import html  # sudo apt install python3-lxml
from lxml.html.clean import Cleaner

import rss_config
import rss_disk
import rss_print


def cleaned_html(htmlString):

    # Try to parse the provided HTML string using lxml
    # strip all unnecessary information to save space
    cleaner = Cleaner()
    cleaner.comments = True
    cleaner.javascript = True
    cleaner.scripts = True
    cleaner.style = True

    htmlString = cleaner.clean_html(htmlString)

    return htmlString


def html_change_short_urls(htmlPageString, curDomainShort):
    """
    Fix short urls.
    """
    htmlPageString = htmlPageString.replace('src="//', 'src="http://')
    htmlPageString = htmlPageString.replace('src="./', 'src="' + curDomainShort + '/')
    htmlPageString = htmlPageString.replace('src="/', 'src="' + curDomainShort + '/')
    htmlPageString = htmlPageString.replace('href="//', 'href="http://')
    htmlPageString = htmlPageString.replace('href="./', 'href="' + curDomainShort + '/')
    htmlPageString = htmlPageString.replace('href="/', 'href="' + curDomainShort + '/')
    rss_print.print_debug(__file__, "html string: " + htmlPageString, 5)

    return htmlPageString


def html_first_node(htmlString):
    htmlStringStartTag = htmlString.split(" ")[0]
    htmlStringStartTag = htmlStringStartTag.split(">")[0]
    htmlStringEndTag = htmlStringStartTag.replace("<", "</") + ">"
    htmlStringList = htmlString.split(htmlStringEndTag)
    countStartTags = htmlStringList[0].count(htmlStringStartTag)

    if countStartTags == 1:
        rss_print.print_debug(__file__, "esimesest splitist leiti " + str(countStartTags) + " esimest tagi '" + htmlStringStartTag + "'", 2)
        htmlString = htmlStringList[0]
        htmlString = htmlString + htmlStringEndTag
    else:
        rss_print.print_debug(__file__, "esimesest splitist leiti " + str(countStartTags) + " esimest tagi '" + htmlStringStartTag + "': " + str(htmlStringList[0]), 1)
        htmlString = htmlStringEndTag.join(htmlStringList[0:countStartTags])
        htmlString = htmlString + htmlStringEndTag

    return htmlString


def html_page_cleanup(htmlString):
    if not htmlString:
        rss_print.print_debug(__file__, "katkestame, tühi sisend: '" + htmlString + "'", 0)
        return htmlString

    rss_print.print_debug(__file__, "puhastame html stringi üleliigsest jamast", 3)

    # remove styles
    htmlString = re.sub(r"<style[\s\S]*?<\/style>", "", htmlString)

    # remove comments
    htmlString = re.sub(r"<!--[\s\S]*?-->", "", htmlString)

    # remove scripts from links
    htmlString = re.sub(r' onclick=(\")[\s\S]*?(\")', "", htmlString)
    htmlString = re.sub(r" onclick=(')[\s\S]*?(')", "", htmlString)

    # remove scripts
    htmlString = re.sub(r"<script[\s\S]*?<\/script>", "", htmlString)

    # remove trackers from links
    htmlString = htmlString.replace("&amp;", "&")
    htmlString = re.sub(r'(&|\?)_[0-9A-Za-z_-]*', "", htmlString)  # delfi
    htmlString = re.sub(r'=2\.[0-9.-]*', "", htmlString)
    htmlString = re.sub(r'_ga=[0-9.-]*', "", htmlString)  # _ga=2.22935807.513285745.1595741966-250801514.1594127878
    htmlString = re.sub(r'fbclid=[0-9A-Za-z-_]*', "", htmlString)
    htmlString = re.sub(r'gclid=[0-9A-Za-z-_]*', "", htmlString)
    htmlString = re.sub(r'refid=[0-9A-Za-z=.%_-]*', "", htmlString)
    htmlString = re.sub(r'utm_source=[0-9A-Za-z-_&=.]*', "", htmlString)

    # fix link without trackers
    htmlString = htmlString.replace("?&", "?")

    # eemaldame html-i vahelise whitespace-i
    htmlString = re.sub(r"\s\s+(?=<)", "", htmlString)

    # eemaldame allesjäänud tühikud
    htmlString = htmlString.replace('\\n', " ")
    htmlString = htmlString.replace('\\r', " ")
    htmlString = htmlString.replace('\\t', " ")

    # br - peab tegema, kuna muidu ei saa xpath oma teekondasid kätte
    htmlString = htmlString.replace("<br/>", "<br>")
    htmlString = htmlString.replace(" <br>", "<br>")
    htmlString = htmlString.replace("<br> ", "<br>")
    htmlString = htmlString.replace("<br><br>", "<br>")

    htmlString = " ".join(htmlString.split())

    return htmlString


def html_remove_single_parents(htmlString):
    i = 0
    while True:
        htmlString = htmlString.strip()

        if not htmlString:
            rss_print.print_debug(__file__, "katkestame, tühi sisend: '" + htmlString + "'", 0)
            return htmlString

        if not htmlString.startswith("<"):
            rss_print.print_debug(__file__, "katkestame, algus pole tag: '" + htmlString + "'", 4)
            return htmlString

        if not htmlString.endswith(">"):
            rss_print.print_debug(__file__, "katkestame, lõpp pole tag: '" + htmlString + "'", 4)
            return htmlString

        if "</" not in htmlString:
            rss_print.print_debug(__file__, "katkestame, puudub lõpptag: '" + htmlString + "'", 4)
            return htmlString

        if htmlString.startswith("<a "):
            rss_print.print_debug(__file__, "katkestame, algus tag on a: '" + htmlString + "'", 4)
            return htmlString

        if htmlString.startswith("<i>"):
            rss_print.print_debug(__file__, "katkestame, algus tag on i: '" + htmlString + "'", 4)
            return htmlString

        if htmlString.startswith("<b>"):
            rss_print.print_debug(__file__, "katkestame, algus tag on b: '" + htmlString + "'", 4)
            return htmlString

        if len(htmlString) <= 7:  # <p></p>
            rss_print.print_debug(__file__, "katkestame, liiga lühike: '" + htmlString + "'", 4)
            return htmlString

        if html_string_count_parent_nodes(htmlString, "html_remove_single_parents") != 1:
            rss_print.print_debug(__file__, "katkestame, mitu parent node-i: '" + htmlString + "'", 4)
            return htmlString

        # so far so good
        i += 1

        # küsime child kandidaadi
        htmlString = html_string_children(htmlString)

        # kui see on tühi, siis teavitame ja lõpetame
        if not htmlString:
            rss_print.print_debug(__file__, "child[" + str(i) + "] hankimise lõpptulemus on tühjus: '" + htmlString + "'", 2)
            return htmlString

        rss_print.print_debug(__file__, "child[" + str(i) + "] hankimise vahetulemus: '" + htmlString + "'", 4)


def html_string_children(htmlString):
    if not isinstance(htmlString, str):
        rss_print.print_debug(__file__, "sisend pole string, tagastame tühjuse", 0)
        return ""

    if htmlString[0] != "<":
        rss_print.print_debug(__file__, "katkestame, algus pole tag: '" + htmlString + "'", 4)
        return htmlString

    if htmlString[-1] != ">":
        rss_print.print_debug(__file__, "katkestame, lõpp pole tag: '" + htmlString + "'", 4)
        return htmlString

    if "</" not in htmlString:
        rss_print.print_debug(__file__, "sisendis pole child elementi, tagastame sisendi", 0)
        return htmlString

    if len(htmlString) <= 7:  # <b></b>
        rss_print.print_debug(__file__, "liiga lühike, tagastame sisendi: '" + htmlString + "'", 0)
        return htmlString

    tagOpening = htmlString.find(">") + 1
    tagClosing = htmlString.rfind("</")

    # lõikame stringist vajaliku osa
    htmlString = htmlString[tagOpening:tagClosing]
    htmlString = htmlString.strip()

    return htmlString


def html_object_count_parent_nodes(htmlTree):
    # loeme ülemobjektid
    parentCount = int(htmlTree.xpath('count(/html/body/*)'))

    return parentCount


def html_string_count_parent_nodes(htmlString, caller):

    htmlString = htmlString.strip()

    if not htmlString:
        return 0

    # loome objektipuu
    htmlTree = html_tree_from_document_string(htmlString, caller)

    # asume lugema ülemobjekte
    parentCount = html_object_count_parent_nodes(htmlTree)

    return parentCount


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


def html_tree_debug(htmlPageName, pageTree):
    """
    Paigutab koodi body elementi ja salvestab selle kettale.
    """
    htmlPageString = html_to_string(pageTree, prettyPrint=True)
    htmlPageString = htmlPageString.split("<body ")[1]
    htmlPageString = htmlPageString.split("</body>")[0]
    htmlPageString = "<body " + htmlPageString + "</body>"
    rss_disk.write_file(rss_config.PATH_FILENAME_DEBUG, htmlPageName, htmlPageString)


def html_tree_from_document_string(htmlString, caller):
    """
    See funktsioon teeb root html treed.
    """
    if caller:
        rss_print.print_debug(__file__, "asume looma html objekti kutsujale: " + caller, 4)

    htmlString = htmlString.strip()
    if not htmlString:
        rss_print.print_debug(__file__, "puudub html stringi sisu kutsujal: '" + caller + "'", 0)
        htmlString = "<html><head></head></html>"

    if htmlString.startswith('<?xml version="1.0" encoding="utf-8"?>'):
        # kui unicode ei käi, proovime utf-8 "Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration."
        htmlStringUtf = htmlString.encode('utf-8')
        htmlTree = html.document_fromstring(htmlStringUtf)
    else:
        try:
            htmlTree = html.document_fromstring(htmlString)
        except Exception as e:
            rss_print.print_debug(__file__, "ei õnnestunud luua mitteutf-8 html objekti kutsujal: '" + caller + "'", 0)
            rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
            rss_print.print_debug(__file__, "ei õnnestunud luua mitteutf-8 html objekti stringist: '" + htmlString + "'", 3)

    return htmlTree


def html_tree_from_string(htmlString, caller):
    """
    See funktsioon ei tee root html treed.
    """
    if caller:
        rss_print.print_debug(__file__, "asume looma html objekti kutsujale: " + caller, 4)

    htmlString = htmlString.strip()
    if not htmlString:
        rss_print.print_debug(__file__, "puudub html stringi sisu kutsujal: '" + caller + "'", 0)

    try:
        htmlTree = html.fromstring(htmlString)
    except Exception as e:
        rss_print.print_debug(__file__, "ei õnnestunud luua mitteutf-8 html objekti kutsujal: '" + caller + "'", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        rss_print.print_debug(__file__, "ei õnnestunud luua mitteutf-8 html objekti stringist: '" + htmlString + "'", 3)

    return htmlTree
