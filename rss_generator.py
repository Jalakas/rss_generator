#!/usr/bin/env python3
"""
    RSS voogude genereerimise käivitaja.
"""

import os
import sys

import requests

import parsers_common
import rss_argv
import rss_config
import rss_disk
import rss_maker
import rss_print
import rss_requests

# manage command line user inputs
RSS_TO_GENERATE = []  # peab olema list tüüpi
RSS_TO_GENERATE = rss_argv.user_inputs(sys.argv, rss_config.RSS_DEFS)
if not RSS_TO_GENERATE:
    RSS_TO_GENERATE = range(len(rss_config.RSS_DEFS))
    if len(sys.argv) > 1:
        rss_print.print_debug(__file__, "ei suutnud sisendist tuvastada sobivat nime, genereeritakse kõik vood.", 0)

# make new session
rss_requests.SESSION = requests.session()

# generate all feeds
for curRSS in RSS_TO_GENERATE:
    curFile = "parser_" + rss_config.RSS_DEFS[curRSS][0]
    curName = rss_config.RSS_DEFS[curRSS][1]
    curTitle = rss_config.RSS_DEFS[curRSS][2]
    curDescription = curTitle + " - " + rss_config.RSS_DEFS[curRSS][3]
    curDomainBeginning = rss_config.RSS_DEFS[curRSS][4]
    curDomainEnds = rss_config.RSS_DEFS[curRSS][5]

    rss_print.print_debug(__file__, "alustame töötlust sisendil[" + str(curRSS) + "]: " + curName, 1)

    # preparations
    __import__(curFile)
    curParser = sys.modules[curFile]
    articleDataDict = {"authors": [], "descriptions": [], "images": [], "pubDates": [], "titles": [], "urls": []}

    for curDomain in curDomainEnds:
        if not curDomain.startswith("http"):
            curDomain = curDomainBeginning + curDomain
            curDomain = parsers_common.str_fix_url_begginning(curDomain)
            rss_print.print_debug(__file__, "curDomain: " + curDomain, 3)

        # get article tree from internet
        rss_print.print_debug(__file__, "asume hankimima lehte: " + curDomain, 2)
        pageTree = parsers_common.get_article_tree(curDomainBeginning, curDomain, cache='cacheOff')

        # get all content from page
        if len(pageTree) > 0:
            rss_print.print_debug(__file__, "asume hankimima sisu lehelt: " + curDomain, 2)
            curArticleDataDict = curParser.fill_article_dict({"authors": [], "descriptions": [], "images": [], "pubDates": [], "titles": [], "urls": []}, pageTree, curDomainBeginning)
        else:
            rss_print.print_debug(__file__, "puudub sisu lehel: " + curDomain, 0)

        # test counts
        parsers_common.dict_stats(curArticleDataDict)

        # lisame viimased andmed
        if curArticleDataDict["urls"]:
            rss_print.print_debug(__file__, "lisame andmed viimaselt alamlehelt: " + curDomain, 2)
            articleDataDict = parsers_common.dict_add_dict(articleDataDict, curArticleDataDict)
        else:
            rss_print.print_debug(__file__, "ei leitud andmeid viimaselt alamlehelt: " + curDomain, 0)

    if not articleDataDict["urls"]:
        rss_print.print_debug(__file__, "ei leitud andmeid lehelt: " + curDomainBeginning, 0)
        continue

    # remove unwanted content: titles
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, rss_config.BAD_TITLES, "in", "titles")

    # remove unwanted content: descriptions
    # articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, rss_config.BAD_DESCRIPTIONS, "in", "descriptions")

    if not articleDataDict["urls"]:
        rss_print.print_debug(__file__, "ei leitud andmeid lehelt: " + curDomain, 0)
        continue

    if not articleDataDict["pubDates"]:
        rss_print.print_debug(__file__, "kuupäevainfota leht: " + curDomain, 1)

    # combine rss file
    rss_print.print_debug(__file__, "asume koostame rss-i: " + curDomain, 3)
    rssContent = rss_maker.rssmaker(articleDataDict, curTitle, curDomainBeginning, curDomain, curDescription)

    # make sure we have subfolder
    OS_PATH = os.path.dirname(os.path.abspath(__file__))
    LATEST_FEEDS_PATH = OS_PATH + "/" + "latest_feeds"
    if not os.path.exists(LATEST_FEEDS_PATH):
        os.makedirs(LATEST_FEEDS_PATH)

    curFilename = curName + ".rss"

    # write feed file
    rss_disk.write_file(LATEST_FEEDS_PATH, curFilename, rssContent)

    # upload feed
    rss_requests.upload_file(LATEST_FEEDS_PATH, curFilename)

# close selenium profile
if rss_config.SELENIUM_DRIVER:
    rss_print.print_debug(__file__, "sulgeme selenium akna(d)", 2)
    rss_config.SELENIUM_DRIVER.quit()
