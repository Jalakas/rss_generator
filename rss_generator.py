#!/usr/bin/env python3

"""
    RSS voogude genereerimise käivitaja
"""

import sys

import os
import random
import requests

import parsers_common
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
import parser_mixcloud  # noqa F401
import parser_nelli  # noqa F401
import parser_nommeraadio  # noqa F401
import parser_osta  # noqa F401
import parser_phpbb  # noqa F401
import parser_postimees  # noqa F401
import parser_ra  # noqa F401
import parser_raadioteater  # noqa F401
import parser_stokker  # noqa F401
import parser_tartuekspress  # noqa F401
import parser_tootukassa  # noqa F401
import parser_trm  # noqa F401
import parser_vbulletin  # noqa F401

RSS_DEFS = []
RSS_TO_GENERATE = []

#                 parser,              name,               title,              description            domain                                  domain_rss (optional)
RSS_DEFS.append(['auto24',            'auto24',           'Auto24',           'foorum',               'http://www.auto24.ee',                 'http://www.auto24.ee/foorum/foorum.php?last_messages=1'])  # noqa E241
RSS_DEFS.append(['avalikteenistus',   'avalikteenistus',  'Avalik teenistus', 'töökohad',             'http://www.rahandusministeerium.ee',   'http://www.rahandusministeerium.ee/et/avalikud-konkursid?page=' + str(random.randint(1, 10))])  # noqa E241
RSS_DEFS.append(['bns',               'bns',              'BNS',              'uudised',              'http://bns.ee',                        ''])  # noqa E241
RSS_DEFS.append(['err',               'err',              'ERR',              'videoarhiiv',          'http://arhiiv.err.ee',                 'http://arhiiv.err.ee/viimati-lisatud/err-videoarhiiv/koik'])  # noqa E241
RSS_DEFS.append(['geopeitus',         'geopeitus',        'Geopeitus',        '"Tartu" aarded',       'http://www.geopeitus.ee',              ''])  # noqa E241
RSS_DEFS.append(['hv',                'hv',               'Hinnavaatlus',     'uudised',              'http://www.hinnavaatlus.ee',           'http://www.hinnavaatlus.ee/#news'])  # noqa E241
RSS_DEFS.append(['kultuuriaken',      'kultuuriaken',     'Kultuuriaken',     'sündmused',            'http://kultuuriaken.tartu.ee',         'http://kultuuriaken.tartu.ee/et/syndmused'])  # noqa E241
RSS_DEFS.append(['lhv',               'lhv',              'LHV',              'foorumipostitused',    'https://fp.lhv.ee',                    'https://fp.lhv.ee/forum/free'])  # noqa E241
RSS_DEFS.append(['mixcloud',          'idaraadio',        'IDA_RAADIO ',      '@mixcloud',            'http://www.mixcloud.com',              'http://www.mixcloud.com/IDA_RAADIO/uploads/?order=latest'])  # noqa E241
RSS_DEFS.append(['mixcloud',          'paranoidtxt',      'paranoidtxt ',     '@mixcloud',            'http://www.mixcloud.com',              'http://www.mixcloud.com/paranoidtxt/uploads/?order=latest'])  # noqa E241
RSS_DEFS.append(['mixcloud',          'rhythmdr',         'rhythmdr ',        '@mixcloud',            'http://www.mixcloud.com',              'http://www.mixcloud.com/rhythmdr/uploads/?order=latest'])  # noqa E241
RSS_DEFS.append(['nelli',             'nelli',            'Nelli Teataja',    'uudised',              'http://www.nelli.ee',                  'http://www.nelli.ee/elu'])  # noqa E241
RSS_DEFS.append(['nommeraadio',       'nommeraadio',      'Nõmme Raadio',     'uudised',              'http://www.nommeraadio.ee',            ''])  # noqa E241
RSS_DEFS.append(['osta',              'ostaee',           'otsa.ee',          'pakkumised',           'http://www.osta.ee',                   'http://www.osta.ee/index.php?fuseaction=search.search&orderby=enda&q[cat]=1397&q[location]=Tartu&start=' + str(random.randint(0, 25)*60)])  # noqa E241
RSS_DEFS.append(['phpbb',             'arutelud',         'Arutelud',         'foorumipostitused',    'http://arutelud.com',                  'http://arutelud.com/search.php?search_id=active_topics'])  # noqa E241
RSS_DEFS.append(['phpbb',             'cbfoorum',         'CB foorum',        'foorumipostitused',    'http://foorum.cbradio.ee',             'http://foorum.cbradio.ee/search.php?search_id=active_topics'])  # noqa E241
RSS_DEFS.append(['phpbb',             'isikee',           'isik.ee',          'foorumipostitused',    'http://www.isik.ee/foorum',            'http://www.isik.ee/foorum/search.php?search_id=active_topics'])  # noqa E241
RSS_DEFS.append(['phpbb',             'militaarnet',      'militaar.net',     'foorumipostitused',    'http://www.militaar.net/phpBB2',       'http://www.militaar.net/phpBB2/search.php?search_id=active_topics'])  # noqa E241
RSS_DEFS.append(['postimees',         'jt',               'Järva Teataja',    'uudised',              'http://jarvateataja.postimees.ee',     'http://jarvateataja.postimees.ee/search'])  # noqa E241
RSS_DEFS.append(['postimees',         'pohjarannik',      'Põhjarannik',      'uudised',              'http://pohjarannik.postimees.ee',      'http://pohjarannik.postimees.ee/search'])  # noqa E241
RSS_DEFS.append(['postimees',         'tartupostimees',   'Tartu Postimees',  'uudised',              'http://tartu.postimees.ee',            'http://tartu.postimees.ee/search'])  # noqa E241
RSS_DEFS.append(['ra',                'ra',               'Rahvusarhiiv',     'uudised',              'http://www.ra.ee',                     'http://www.ra.ee/uudised'])  # noqa E241
RSS_DEFS.append(['raadioteater',      'kuuldemangud',     'Raadioteater',     'kuuldemängud',         'http://raadioteater.err.ee',           'http://raadioteater.err.ee/raadioteater/kuuldemaengarhiiv'])  # noqa E241
RSS_DEFS.append(['stokker',           'stokker',          'Stokker',          'outlet pakkumised',    'http://www.stokker.ee',                'http://www.stokker.ee/kampaaniad/tooriistade-outlet?page=' + str(random.randint(1, 15)) + '&limit=' + str(rss_config.MAX_ARTICLE_BODIES) + '&instorage=1'])  # noqa E241
RSS_DEFS.append(['tartuekspress',     'tartuekspress',    'Tartu Ekspress',   'uudised',              'http://tartuekspress.ee',              'http://tartuekspress.ee/index.php?page=20&type=3'])  # noqa E241
RSS_DEFS.append(['tootukassa',        'tootukassa',       'Töötukassa',       'tööpakkumised',        'http://www.tootukassa.ee',             'http://www.tootukassa.ee/toopakkumised?asukohad%5B%5D=EE%2F79&asukohad%5B%5D=EE%2F52&haridustase%5Bmin%5D=KUTSEKORGHARIDUS&haridustase%5Bmax%5D=MAGISTRIOPE'])  # noqa E241
RSS_DEFS.append(['trm',               'tooriistamarket',  'Tööriistamarket',  'head pakkumised',      'http://www.tooriistamarket.ee',        'http://www.tooriistamarket.ee/et/head-pakkumised?price=1&page=' + str(random.randint(0, 20))])  # noqa E241
RSS_DEFS.append(['vbulletin',         'elfafoorum',       'ELFA',             'foorum',               'http://www.elfafoorum.ee',             'https://www.elfafoorum.ee/search.php?do=getdaily'])  # noqa E241


# user input
for i in range(1, len(sys.argv)):
    curSisend = str(sys.argv[i])
    curSisendArg = curSisend.split("=")[0]

    if curSisendArg == "-limit":
        rss_config.MAX_ARTICLE_BODIES = int(curSisend.split("=")[1])
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif curSisend == "-nocache":
        rss_config.ARTICLE_CACHE_POLICY = 'off'
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif curSisend == "-cache":
        rss_config.ARTICLE_CACHE_POLICY = 'all'
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif curSisend == "-v":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 1)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif curSisend == "-vv":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 2)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif curSisend == "-vvv":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 3)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif curSisend == "-vvvv":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 4)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif curSisend == "-vvvvv":
        rss_print.PRINT_MESSAGE_LEVEL = max(rss_print.PRINT_MESSAGE_LEVEL, 5)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 0)
    elif curSisend != "":
        for j, rss_def in enumerate(RSS_DEFS):
            if curSisend == rss_def[1]:
                RSS_TO_GENERATE.append(j)
                rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 1)
                # tühjendame hilisema kontrolli jaoks
                curSisend = ""
                break
        # kui for-is ei leitud
        if curSisend != "":
            rss_print.print_debug(__file__, 'tundmatu sisend: "' + curSisend + '"', 0)


if not RSS_TO_GENERATE:
    RSS_TO_GENERATE = range(len(RSS_DEFS))
    if len(sys.argv) > 1:
        rss_print.print_debug(__file__, "ei suutnud sisendist tuvastada sobivat nime, genereeritakse kõik vood.", 0)

# make new session
SESSION = requests.session()

# generate all feeds
for curRSS in RSS_TO_GENERATE:
    curParser = sys.modules['parser_' + RSS_DEFS[curRSS][0]]
    curName = RSS_DEFS[curRSS][1]
    curTitle = RSS_DEFS[curRSS][2]
    curDescription = RSS_DEFS[curRSS][2] + " - " + RSS_DEFS[curRSS][3]
    curDomainShort = curDomainLong = RSS_DEFS[curRSS][4].replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')
    if len(RSS_DEFS[curRSS]) > 4 and RSS_DEFS[curRSS][5]:
        curDomainLong = RSS_DEFS[curRSS][5]

    # preparations
    curFilename = curName + '.rss'
    articleDataDictEmpty = {"authors": [], "descriptions": [], "images": [], "pubDates": [], "titles": [], "urls": []}

    # hangime alati lehe sisu
    rss_print.print_debug(__file__, "asume internetist pärima lehte: " + curDomainLong, 2)
    pageHtmlString = parsers_common.get_article_string(SESSION, curDomainShort, curDomainLong, noCache=True)

    # puhastab lehe üleliigsest jamast
    pageHtmlString = parsers_common.html_string_cleanup(pageHtmlString)

    # load page string into tree
    rss_print.print_debug(__file__, "asume looma html objekti: " + curDomainLong, 2)
    articleHtmlTree = parsers_common.html_tree_from_string(pageHtmlString, curDomainLong)

    # get all content from page
    rss_print.print_debug(__file__, "asume sisu hankimima: " + curDomainLong, 2)
    articleDataDict = curParser.fill_article_dict(articleDataDictEmpty, articleHtmlTree, curDomainShort, curDomainLong, SESSION)

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
    rss_print.print_debug(__file__, "asume koostame rss-i: " + curDomainLong, 2)
    rss_content = rss_maker.rssmaker(articleDataDict, curTitle, curDomainShort, curDomainLong, curDescription)

    # make sure we have subfolders
    OS_PATH = os.path.dirname(os.path.abspath(__file__))
    LATEST_FEEDS_PATH = OS_PATH + '/' + 'latest_feeds'
    OLDER_FEEDS_PATH = OS_PATH + '/' + 'older_feeds'
    if not os.path.exists(LATEST_FEEDS_PATH):
        os.makedirs(LATEST_FEEDS_PATH)
    if not os.path.exists(OLDER_FEEDS_PATH):
        os.makedirs(OLDER_FEEDS_PATH)
    curFilenameFull = LATEST_FEEDS_PATH + '/' + curFilename
    destFilenameFull = OLDER_FEEDS_PATH + '/' + curFilename

    # move away old feed, if there is any
    rss_print.print_debug(__file__, "asume liigutame faili: " + curFilenameFull + "->" + destFilenameFull, 2)
    rss_disk.rename_file(curFilenameFull, destFilenameFull)

    # write feed
    rss_print.print_debug(__file__, "asume salvestame faili: " + curFilenameFull, 2)
    rss_disk.save_file(curFilenameFull, rss_content)

    # upload feed
    rss_print.print_debug(__file__, "asume faili üles laadima: " + curFilenameFull, 2)
    rss_makereq.upload_file(curFilename, curFilenameFull)
