#!/usr/bin/env python3

"""
    RSS voogude genereerimise käivitaja
"""

import os
import requests
import sys

import parsers_common
import rss_argv
import rss_config
import rss_disk
import rss_maker
import rss_makereq
import rss_print

import parser_auto24  # noqa F401
import parser_avalikteenistus  # noqa F401
import parser_bns  # noqa F401
import parser_err  # noqa F401
import parser_geopeitus  # noqa F401
import parser_hv  # noqa F401
import parser_kultuuriaken  # noqa F401
import parser_lhv  # noqa F401
import parser_lineageos  # noqa F401
import parser_mixcloud  # noqa F401
import parser_nelli  # noqa F401
import parser_nommeraadio  # noqa F401
import parser_osta  # noqa F401
import parser_perekool  # noqa F401
import parser_phpbb  # noqa F401
import parser_postimees  # noqa F401
import parser_ra  # noqa F401
import parser_raadioteater  # noqa F401
import parser_stokker  # noqa F401
import parser_tartuekspress  # noqa F401
import parser_tootukassa  # noqa F401
import parser_trm  # noqa F401
import parser_tv3  # noqa F401
import parser_vbulletin  # noqa F401
import parser_youtube  # noqa F401

# manage command line user inputs
RSS_TO_GENERATE = []
RSS_TO_GENERATE = rss_argv.user_inputs(sys.argv, rss_config.RSS_DEFS)
if not RSS_TO_GENERATE:
    RSS_TO_GENERATE = range(len(rss_config.RSS_DEFS))
    if len(sys.argv) > 1:
        rss_print.print_debug(__file__, "ei suutnud sisendist tuvastada sobivat nime, genereeritakse kõik vood.", 0)

# make new session
SESSION = requests.session()

# generate all feeds
for curRSS in RSS_TO_GENERATE:
    curParser = sys.modules['parser_' + rss_config.RSS_DEFS[curRSS][0]]
    curName = rss_config.RSS_DEFS[curRSS][1]
    curTitle = rss_config.RSS_DEFS[curRSS][2]
    curDescription = rss_config.RSS_DEFS[curRSS][2] + " - " + rss_config.RSS_DEFS[curRSS][3]
    curDomainShort = rss_config.RSS_DEFS[curRSS][4]
    curDomainShort = parsers_common.rchop(curDomainShort, "/")
    curDomainShort = curDomainShort.replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')
    if len(rss_config.RSS_DEFS[curRSS]) > 4 and rss_config.RSS_DEFS[curRSS][5]:
        curDomainLong = rss_config.RSS_DEFS[curRSS][5]
    else:
        curDomainLong = curDomainShort

    # preparations
    curFilename = curName + '.rss'
    articleDataDictEmpty = {"authors": [], "descriptions": [], "images": [], "pubDates": [], "titles": [], "urls": []}

    # get article tree from internet
    rss_print.print_debug(__file__, "asume lehte hankimima: " + curDomainLong, 2)
    articleHtmlTree = parsers_common.get_article_tree(SESSION, curDomainShort, curDomainLong, noCache=True)

    # get all content from page
    rss_print.print_debug(__file__, "asume lehelt sisu hankimima: " + curDomainLong, 2)
    articleDataDict = curParser.fill_article_dict(articleDataDictEmpty, articleHtmlTree, curDomainShort, curDomainLong, SESSION)

    lastValueCount = 0
    lastValueName = ""
    for x in articleDataDict:
        curValueCount = len(articleDataDict[x])
        curValueName = str(x)

        if (lastValueCount != 0 and curValueCount != 0 and lastValueCount != curValueCount):
            rss_print.print_debug(__file__, "'" + curValueName + "' väärtuste arv: " + str(curValueCount) + " ei kattu eelmisega '" + lastValueName + "':" + str(lastValueCount), 0)
        elif curValueName == "urls" and curValueCount == 0:
            rss_print.print_debug(__file__, "'" + curValueName + "' väärtuste arv: " + str(curValueCount), 0)
        elif curValueName == "urls":
            rss_print.print_debug(__file__, "'" + curValueName + "' väärtuste arv: " + str(curValueCount), 1)
        else:
            rss_print.print_debug(__file__, "'" + curValueName + "' väärtuste arv: " + str(curValueCount), 2)

        rss_print.print_debug(__file__, "'" + curValueName + "' = " + str(articleDataDict[x]), 3)

        lastValueCount = curValueCount
        lastValueName = curValueName

    # combine rss file
    rss_content = rss_maker.rssmaker(articleDataDict, curTitle, curDomainShort, curDomainLong, curDescription)

    # make sure we have subfolder
    OS_PATH = os.path.dirname(os.path.abspath(__file__))
    LATEST_FEEDS_PATH = OS_PATH + '/' + 'latest_feeds'
    if not os.path.exists(LATEST_FEEDS_PATH):
        os.makedirs(LATEST_FEEDS_PATH)

    # move away old feed, if there is any
    rss_disk.rename_file(LATEST_FEEDS_PATH, curFilename)

    # write feed file
    rss_disk.write_file(LATEST_FEEDS_PATH, curFilename, rss_content)

    # upload feed
    rss_makereq.upload_file(LATEST_FEEDS_PATH, curFilename)
