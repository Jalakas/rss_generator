#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS voogude genereerimise käivitaja
"""

import os
import random
import sys
import requests

import parsers_common
import rss_config
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
import parser_mixcloud  # noqa F401
import parser_nelli  # noqa F401
import parser_nommeraadio  # noqa F401
import parser_osta  # noqa F401
import parser_phpbb  # noqa F401
import parser_phpbb2  # noqa F401
import parser_postimees  # noqa F401
import parser_ra  # noqa F401
import parser_raadioteater  # noqa F401
import parser_stokker  # noqa F401
import parser_tartuekspress  # noqa F401
import parser_tootukassa  # noqa F401
import parser_trm  # noqa F401

# definitions
MAX_ARTICLE_BODIES = 200
GER_ARTICLE_BODIES = True

OS_PATH = os.path.dirname(os.path.abspath(__file__))
LATEST_FEEDS_PATH = OS_PATH + '/' + 'latest_feeds'
OLDER_FEEDS_PATH = OS_PATH + '/' + 'older_feeds'

RSS_DEFS = []
RSS_TO_GENERATE = []

#                 parser,              name,               title,              description            domain                                  domain_rss (optional)
RSS_DEFS.append(['auto24',            'auto24',           'Auto24',           'foorum',               '',                                     'https://www.auto24.ee/foorum/foorum.php?last_messages=1'])  # noqa E241
RSS_DEFS.append(['avalikteenistus',   'avalikteenistus',  'Avalik teenistus', 'töökohad',             'http://www.rahandusministeerium.ee',   'http://www.rahandusministeerium.ee/et/avalikud-konkursid?page=' + str(random.randint(1, 12))])  # noqa E241
RSS_DEFS.append(['bns',               'bns',              'BNS',              'uudised',              'http://bns.ee',                        ''])  # noqa E241
RSS_DEFS.append(['err',               'err',              'ERR',              'videoarhiiv',          'http://arhiiv.err.ee',                 'https://arhiiv.err.ee/viimati-lisatud/err-videoarhiiv/koik'])  # noqa E241
RSS_DEFS.append(['geopeitus',         'geopeitus',        'Geopeitus',        '"Tartu" aarded',       'http://www.geopeitus.ee',              ''])  # noqa E241
RSS_DEFS.append(['hv',                'hv',               'Hinnavaatlus',     'uudised',              'http://www.hinnavaatlus.ee',           'http://www.hinnavaatlus.ee/#news'])  # noqa E241
RSS_DEFS.append(['kultuuriaken',      'kultuuriaken',     'Kultuuriaken',     'sündmused',            'http://kultuuriaken.tartu.ee',         'http://kultuuriaken.tartu.ee/et/syndmused'])  # noqa E241
RSS_DEFS.append(['lhv',               'lhv',              'LHV',              'foorumipostitused',    'https://fp.lhv.ee',                    'https://fp.lhv.ee/forum/free'])  # noqa E241
RSS_DEFS.append(['mixcloud',          'idaraadio',        'IDA_RAADIO ',      '@mixcloud',            'https://www.mixcloud.com',             'http://www.mixcloud.com/IDA_RAADIO/uploads/?order=latest'])  # noqa E241
RSS_DEFS.append(['mixcloud',          'paranoidtxt',      'paranoidtxt ',     '@mixcloud',            'https://www.mixcloud.com',             'http://www.mixcloud.com/paranoidtxt/uploads/?order=latest'])  # noqa E241
RSS_DEFS.append(['mixcloud',          'rhythmdr',         'rhythmdr ',        '@mixcloud',            'https://www.mixcloud.com',             'http://www.mixcloud.com/rhythmdr/uploads/?order=latest'])  # noqa E241
RSS_DEFS.append(['nelli',             'nelli',            'Nelli Teataja',    'uudised',              'http://www.nelli.ee',                  'http://www.nelli.ee/elu'])  # noqa E241
RSS_DEFS.append(['nommeraadio',       'nommeraadio',      'Nõmme Raadio',     'uudised',              'http://www.nommeraadio.ee',            ''])  # noqa E241
RSS_DEFS.append(['osta',              'ostaee',           'otsa.ee',          'pakkumised',           'https://www.osta.ee',                  'http://www.osta.ee/index.php?fuseaction=search.search&orderby=enda&q[cat]=1397&q[location]=Tartu&start=' + str(random.randint(0, 25)*60)])  # noqa E241
RSS_DEFS.append(['phpbb',             'arutelud',         'Arutelud',         'foorumipostitused',    'http://arutelud.com',                  'http://arutelud.com/search.php?search_id=active_topics'])  # noqa E241
RSS_DEFS.append(['phpbb',             'cbfoorum',         'CB foorum',        'foorumipostitused',    'http://foorum.cbradio.ee',             'http://foorum.cbradio.ee/search.php?search_id=active_topics'])  # noqa E241
RSS_DEFS.append(['phpbb',             'isikee',           'isik.ee',          'foorumipostitused',    'http://www.isik.ee/foorum',            'http://www.isik.ee/foorum/search.php?search_id=active_topics'])  # noqa E241
RSS_DEFS.append(['phpbb2',            'militaarnet',      'militaar.net',     'foorumipostitused',    'http://www.militaar.net/phpBB2',       'http://www.militaar.net/phpBB2/search.php?search_id=active_topics'])  # noqa E241
RSS_DEFS.append(['postimees',         'jt',               'Järva Teataja',    'uudised',              'http://jarvateataja.postimees.ee',     'http://jarvateataja.postimees.ee/search'])  # noqa E241
RSS_DEFS.append(['postimees',         'pohjarannik',      'Põhjarannik',      'uudised',              'http://pohjarannik.postimees.ee',      'http://pohjarannik.postimees.ee/search'])  # noqa E241
RSS_DEFS.append(['postimees',         'tartupostimees',   'Tartu Postimees',  'uudised',              'http://tartu.postimees.ee',            'http://tartu.postimees.ee/search'])  # noqa E241
RSS_DEFS.append(['ra',                'ra',               'Rahvusarhiiv',     'uudised',              'http://www.ra.ee',                     'http://www.ra.ee/uudised'])  # noqa E241
RSS_DEFS.append(['raadioteater',      'kuuldemangud',     'Raadioteater',     'kuuldemängud',         'http://raadioteater.err.ee',           'http://raadioteater.err.ee/raadioteater/kuuldemaengarhiiv'])  # noqa E241
RSS_DEFS.append(['stokker',           'stokker',          'Stokker',          'outlet pakkumised',    'http://www.stokker.ee',                'http://www.stokker.ee/kampaaniad/tooriistade-outlet?page=' + str(random.randint(1, 15)) + '&limit=' + str(MAX_ARTICLE_BODIES) + '&instorage=1'])  # noqa E241
RSS_DEFS.append(['tartuekspress',     'tartuekspress',    'Tartu Ekspress',   'uudised',              'http://tartuekspress.ee',              'http://tartuekspress.ee/index.php?page=20&type=3'])  # noqa E241
RSS_DEFS.append(['tootukassa',        'tootukassa',       'Töötukassa',       'tööpakkumised',        'http://www.tootukassa.ee',             'https://www.tootukassa.ee/toopakkumised?asukohad%5B%5D=EE%2F79&asukohad%5B%5D=EE%2F52&haridustase%5Bmin%5D=KUTSEKORGHARIDUS&haridustase%5Bmax%5D=MAGISTRIOPE'])  # noqa E241
RSS_DEFS.append(['trm',               'tooriistamarket',  'Tööriistamarket',  'head pakkumised',      'http://www.tooriistamarket.ee',        'http://www.tooriistamarket.ee/et/head-pakkumised?price=1&page=' + str(random.randint(0, 20))])  # noqa E241

# user input
for i in range(1, len(sys.argv)):
    curSisend = sys.argv[i]
    curSisendArg = curSisend.split("=")[0]

    if str(curSisendArg) == "-limit":
        MAX_ARTICLE_BODIES = int(curSisend.split("=")[1])
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif str(curSisendArg) == "-devel":
        rss_makereq.cacheMainArticleBodies = True
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif str(curSisend) == "-v":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 1)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif str(curSisend) == "-vv":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 2)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif str(curSisend) == "-vvv":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 3)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif str(curSisend) == "-vvvv":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 4)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif str(curSisend) == "-vvvvv":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 5)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif str(curSisend) != "":
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 1)
        for j, rss_def in enumerate(RSS_DEFS):
            if (curSisend == rss_def[1]):
                RSS_TO_GENERATE.append(j)
                break

if not RSS_TO_GENERATE:
    RSS_TO_GENERATE = range(0, len(RSS_DEFS))
    if len(sys.argv) > 1:
        rss_print.print_debug(__file__, "ei suutnud sisendist tuvastada sobivat nime, genereeritakse kõik vood.", 0)

# make sure we have subfolders
if not os.path.exists(LATEST_FEEDS_PATH):
    os.makedirs(LATEST_FEEDS_PATH)
if not os.path.exists(OLDER_FEEDS_PATH):
    os.makedirs(OLDER_FEEDS_PATH)

# generate all feeds
for curRSS in RSS_TO_GENERATE:

    curParser = sys.modules['parser_' + RSS_DEFS[curRSS][0]]
    curName = RSS_DEFS[curRSS][1]
    curTitle = RSS_DEFS[curRSS][2]
    curDescription = RSS_DEFS[curRSS][2] + " - " + RSS_DEFS[curRSS][3]
    curDomain = curDomainRSS = RSS_DEFS[curRSS][4].replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')
    if len(RSS_DEFS[curRSS]) > 4 and RSS_DEFS[curRSS][5]:
        curDomainRSS = RSS_DEFS[curRSS][5]

    curFilename = curName + '.rss'
    curFilenameFull = LATEST_FEEDS_PATH + '/' + curFilename
    destFilenameFull = OLDER_FEEDS_PATH + '/' + curFilename

    # load page into tree
    try:
        rss_print.print_debug(__file__, "pärime lehe: " + curDomainRSS, 2)
        pageHtmlTree = rss_makereq.get_article_data(curDomainRSS, mainPage=True)
        rss_print.print_debug(__file__, parsers_common.elemtree_to_string(pageHtmlTree), 5)
    except Exception as e:
        rss_print.print_debug(__file__, "Viga! Ei suutnud andmeid pärida leheküljelt: " + curDomainRSS, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        continue

    # get all content from page
    rss_print.print_debug(__file__, "alustame sisu parsimist: " + str(curDomainRSS), 2)
    articleDataDictEmpty = {"authors": [], "descriptions": [], "images": [], "pubDates": [], "titles": [], "urls": []}
    articleDataDict = curParser.article_dict(articleDataDictEmpty, pageHtmlTree, curDomain, MAX_ARTICLE_BODIES, GER_ARTICLE_BODIES)

    rss_print.print_debug(__file__, "articleDataDict = " + str(articleDataDict), 4)

    lastValueCount = 0
    lastValueName = ""
    for x in articleDataDict:
        curValueCount = len(articleDataDict[x])
        curValueName = str(x)

        rss_print.print_debug(__file__, curValueName + "=" + str(articleDataDict[x]), 3)

        if (lastValueCount != 0 and curValueCount != 0 and lastValueCount != curValueCount):
            rss_print.print_debug(__file__, "'" + curValueName + "' väärtuste arv: " + str(curValueCount) + " ei kattu eelmisega '" + lastValueName + "':" + str(lastValueCount), 0)
        elif curValueName == "urls" and curValueCount == 0:
            rss_print.print_debug(__file__, "'" + curValueName + "' väärtuste arv: " + str(curValueCount), 0)
        elif curValueName == "urls":
            rss_print.print_debug(__file__, "'" + curValueName + "' väärtuste arv: " + str(curValueCount), 1)
        else:
            rss_print.print_debug(__file__, "'" + curValueName + "' väärtuste arv: " + str(curValueCount), 2)
        lastValueCount = curValueCount
        lastValueName = curValueName

    # combine rss file
    rss_print.print_debug(__file__, "koostame rss-i: " + curDomainRSS, 2)
    rss_content = rss_maker.rssmaker(articleDataDict, curTitle, curDomain, curDomainRSS, curDescription, rss_config.HOST_URL + "/" + curFilename)

    # move away old feed, if there is any
    try:
        os.rename(curFilenameFull, destFilenameFull)
        rss_print.print_debug(__file__, "faili liigutamine õnnestus: " + curFilenameFull + "->" + destFilenameFull, 2)
    except Exception as e:
        rss_print.print_debug(__file__, "faili liigutamine EBAõnnestus: " + curFilenameFull + "->" + destFilenameFull, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

    # write feed
    try:
        rss_content.write(open(curFilenameFull, 'wb'), encoding='UTF-8', pretty_print=True)
        rss_print.print_debug(__file__, "faili salvestamine õnnestus: " + curFilenameFull, 2)
    except Exception as e:
        rss_print.print_debug(__file__, "faili salvestamine EBAõnnestus: " + curFilenameFull, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

    # upload feed
    try:
        files = {rss_config.UPLOAD_NAME: open(curFilenameFull, 'rb')}
        reply = requests.post(rss_config.UPLOAD_URL, files=files)

        rss_print.print_debug(__file__, "reply.status_code: " + str(reply.status_code), 3)
        if (reply.status_code == 200):
            rss_print.print_debug(__file__, "faili üleslaadimine õnnestus: " + curFilename, 2)
        else:
            rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + curFilename, 0)
            rss_print.print_debug(__file__, "serveri vastus: " + str(reply.text), 2)
    except Exception as e:
        rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + curFilename, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
