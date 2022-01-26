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
RSS_TO_GENERATE = []
RSS_TO_GENERATE = rss_argv.user_inputs(sys.argv, rss_config.RSS_DEFS)
if not RSS_TO_GENERATE:
    RSS_TO_GENERATE = range(len(rss_config.RSS_DEFS))
    if len(sys.argv) > 1:
        rss_print.print_debug(__file__, "ei suutnud sisendist tuvastada sobivat nime, genereeritakse kõik vood.", 0)

# make new session
rss_requests.SESSION = requests.session()

# generate all feeds
for curRSS in RSS_TO_GENERATE:
    __import__("parser_" + rss_config.RSS_DEFS[curRSS][0])
    curParser = sys.modules["parser_" + rss_config.RSS_DEFS[curRSS][0]]
    curName = rss_config.RSS_DEFS[curRSS][1]
    rss_print.print_debug(__file__, "alustame töötlust sisendil[" + str(curRSS) + "]: " + curName, 1)
    curTitle = rss_config.RSS_DEFS[curRSS][2]
    curDescription = rss_config.RSS_DEFS[curRSS][2] + " - " + rss_config.RSS_DEFS[curRSS][3]
    curDomainShort = rss_config.RSS_DEFS[curRSS][4]
    curDomainShort = parsers_common.str_rchop(curDomainShort, "/")
    curDomainShort = parsers_common.str_fix_url_begginning(curDomainShort)
    if len(rss_config.RSS_DEFS[curRSS]) > 4 and rss_config.RSS_DEFS[curRSS][5]:
        curDomainsLong = rss_config.RSS_DEFS[curRSS][5]
    else:
        curDomainsLong = [curDomainShort]

    # preparations
    curFilename = curName + ".rss"
    articleDataDict = {"authors": [], "descriptions": [], "images": [], "pubDates": [], "titles": [], "urls": []}

    for curDomainLong in curDomainsLong:
        if not curDomainLong.startswith("http"):
            rss_print.print_debug(__file__, "lühivorm curDomainLong: " + curDomainLong, 2)
            curDomainLong = curDomainShort + curDomainLong
            curDomainLong = parsers_common.str_fix_url_begginning(curDomainLong)

        # get article tree from internet
        rss_print.print_debug(__file__, "asume hankimima lehte: " + curDomainLong, 2)
        pageTree = parsers_common.get_article_tree(curDomainShort, curDomainLong, cache='cacheOff')

        # get all content from page
        rss_print.print_debug(__file__, "asume sisu hankimima lehelt: " + curDomainLong, 2)
        curArticleDataDict = curParser.fill_article_dict({"authors": [], "descriptions": [], "images": [], "pubDates": [], "titles": [], "urls": []}, pageTree, curDomainShort)

        # test counts
        parsers_common.dict_stats(curArticleDataDict)

        # lisame viimased andmed
        rss_print.print_debug(__file__, "lisame andmed viimaselt alamlehelt: " + curDomainLong, 2)
        articleDataDict = parsers_common.dict_add_dict(articleDataDict, curArticleDataDict)

    if not articleDataDict["urls"]:
        rss_print.print_debug(__file__, "ei leitud andmeid lehelt: " + curDomainShort, 0)
        continue

    # remove unwanted content: titles
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, rss_config.BAD_TITLES, "in", "titles")

    # remove unwanted content: descriptions
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, rss_config.BAD_DESCRIPTIONS, "in", "descriptions")

    # combine rss file
    rss_print.print_debug(__file__, "asume koostame rss-i: " + curDomainLong, 3)
    rssContent = rss_maker.rssmaker(articleDataDict, curTitle, curDomainShort, curDomainLong, curDescription)

    # make sure we have subfolder
    OS_PATH = os.path.dirname(os.path.abspath(__file__))
    LATEST_FEEDS_PATH = OS_PATH + "/" + "latest_feeds"
    if not os.path.exists(LATEST_FEEDS_PATH):
        os.makedirs(LATEST_FEEDS_PATH)

    # write feed file
    rss_disk.write_file(LATEST_FEEDS_PATH, curFilename, rssContent)

    # upload feed
    rss_requests.upload_file(LATEST_FEEDS_PATH, curFilename)

# close selenium profile
if rss_config.SELENIUM_DRIVER_DEFAULT != "":
    rss_print.print_debug(__file__, "sulgeme selenium akna(d)", 2)
    rss_config.SELENIUM_DRIVER_DEFAULT.quit()
