#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS voogude genereerimise käivitaja
"""

import os
import sys
import requests

import rss_config
import parsers_common
import rss_maker
import rss_print

import parser_arutelud  # noqa F401
import parser_avalikteenistus  # noqa F401
import parser_bns  # noqa F401
import parser_geopeitus  # noqa F401
import parser_hv  # noqa F401
# import parser_kultuuriaken  # noqa F401
import parser_lhv  # noqa F401
import parser_mixcloud  # noqa F401
import parser_nommeraadio  # noqa F401
import parser_postimees  # noqa F401
import parser_ra  # noqa F401
import parser_raadioteater  # noqa F401
import parser_stokker  # noqa F401
import parser_tartuekspress  # noqa F401
import parser_tootukassa  # noqa F401
import parser_trm  # noqa F401

# definitions
maxArticleCount = 200
getArticleBodies = True

osPath = os.path.dirname(os.path.abspath(__file__))
latestFeedsPath = osPath + '/' + 'latest_feeds'
oldersFeedsPath = osPath + '/' + 'older_feeds'

RSSdefinitions = []
RSStoGenerate = []
sisend = ['', '', '', '']

#                       parser,              name,               title,              description        domain                                  domain_rss (optional)
RSSdefinitions.append(['arutelud',          'arutelud',         'Arutelud',         'foorumipostitused','http://arutelud.com',                  'http://arutelud.com/viewtopic.php?f=3&t=4&sd=d&sk=t&st=7'])  # noqa E241
RSSdefinitions.append(['avalikteenistus',   'avalikteenistus',  'Avalik teenistus', '"Tartu" töökohad', 'http://www.rahandusministeerium.ee',   'http://www.rahandusministeerium.ee/et/avalikud-konkursid?page=1'])  # noqa E241
RSSdefinitions.append(['bns',               'bns',              'BNS',              'uudised',          'http://bns.ee',                        ''])  # noqa E241
RSSdefinitions.append(['geopeitus',         'geopeitus',        'Geopeitus',        '"Tartu" aarded',   'http://www.geopeitus.ee',              ''])  # noqa E241
RSSdefinitions.append(['hv',                'hv',               'Hinnavaatlus',     'uudised',          'http://www.hinnavaatlus.ee',           'http://www.hinnavaatlus.ee/#news'])  # noqa E241
# java või ajaxi uuenev käkk
# RSSdefinitions.append(['kultuuriaken',    'kultuuriaken',     'Kultuuriaken',     'sündmused',        'http://kultuuriaken.tartu.ee',         'http://kultuuriaken.tartu.ee/et/syndmused?category_1=all|40|41|42|43|44|52&category_2=all|45|46|47|48|49|50|51|53&category_7=all&category_3=all&category_8=all&category_54=all&category_4=all&category_5=all&category_6=all&category_9=all&region=Tartu|78|LE&starting_time=1&filter-button=9'])  # noqa E241
RSSdefinitions.append(['lhv',               'lhv',              'LHV',              'foorumipostitused','https://fp.lhv.ee',                    'https://fp.lhv.ee/forum/free'])  # noqa E241
RSSdefinitions.append(['mixcloud',          'idaraadio',        'Mixcloud(IDA_RAADIO)', '',             'https://www.mixcloud.com',             'http://www.mixcloud.com/IDA_RAADIO/uploads/?order=latest'])  # noqa E241
RSSdefinitions.append(['mixcloud',          'paranoidtxt',      'Mixcloud(paranoidtxt)','',             'https://www.mixcloud.com',             'http://www.mixcloud.com/paranoidtxt'])  # noqa E241
RSSdefinitions.append(['mixcloud',          'rhythmdr',         'Mixcloud(rhythmdr)',   '',             'https://www.mixcloud.com',             'http://www.mixcloud.com/rhythmdr'])  # noqa E241
RSSdefinitions.append(['nommeraadio',       'nommeraadio',      'Nõmme Raadio',     'uudised',          'http://www.nommeraadio.ee',            ''])  # noqa E241
RSSdefinitions.append(['postimees',         'jt',               'Järva Teataja',    'uudised',          'http://jarvateataja.postimees.ee',     'http://jarvateataja.postimees.ee/search'])  # noqa E241
RSSdefinitions.append(['postimees',         'pohjarannik',      'Põhjarannik',      'uudised',          'http://pohjarannik.postimees.ee',      'http://pohjarannik.postimees.ee/search'])  # noqa E241
RSSdefinitions.append(['postimees',         'tartupostimees',   'Tartu Postimees',  'uudised',          'http://tartu.postimees.ee',            'http://tartu.postimees.ee/search'])  # noqa E241
RSSdefinitions.append(['ra',                'ra',               'Rahvusarhiiv',     'uudised',          'http://www.ra.ee',                     'http://www.ra.ee/uudised'])  # noqa E241
RSSdefinitions.append(['raadioteater',      'kuuldemangud',     'Raadioteater',     'kuuldemängud',     'http://raadioteater.err.ee',           'http://raadioteater.err.ee/raadioteater/kuuldemaengarhiiv'])  # noqa E241
RSSdefinitions.append(['stokker',           'stokker',          'Stokker',          'outlet pakkumised','http://www.stokker.ee',                'http://www.stokker.ee/kampaaniad/tooriistade-outlet?page=1&limit='+ str(maxArticleCount) +'&orderby=price&orderdir=asc&instorage=1'])  # noqa E241
RSSdefinitions.append(['tartuekspress',     'tartuekspress',    'Tartu Ekspress',   'uudised',          'http://tartuekspress.ee',              'http://tartuekspress.ee/index.php?page=20&type=3'])  # noqa E241
RSSdefinitions.append(['tootukassa',        'tootukassa',       'Töötukassa',       'tööpakkumised',    'http://www.tootukassa.ee',             'http://www.tootukassa.ee/toopakkumised?asukohad%5B%5D=EE%2F79&asukohad%5B%5D=EE%2F52&haridustase%5Bmin%5D=KUTSEKORGHARIDUS&haridustase%5Bmax%5D=DOKTORIOPE&tooaeg=KOIK&vahetustega=KOIK&varasemTookogemusAastaidMaks=10'])  # noqa E241
RSSdefinitions.append(['trm',               'tooriistamarket',  'Tööriistamarket',  'head pakkumised',  'http://www.tooriistamarket.ee',        'http://www.tooriistamarket.ee/et/head-pakkumised?price=1&page=1'])  # noqa E241


# user input
for i in range(1, len(sys.argv)):
    curSisend = sys.argv[i]
    curSisendArg = curSisend.split("=")[0]

    if str(curSisendArg) == "-limit":
        maxArticleCount = int(curSisend.split("=")[1])
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"')
    elif str(curSisend) == "-v":
        rss_print.printDebugMessageLevel = max(rss_print.printDebugMessageLevel, 1)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"')
    elif str(curSisend) == "-vv":
        rss_print.printDebugMessageLevel = max(rss_print.printDebugMessageLevel, 2)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"')
    elif str(curSisend) == "-vvv":
        rss_print.printDebugMessageLevel = max(rss_print.printDebugMessageLevel, 3)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"')
    elif str(curSisend) == "-vvvv":
        rss_print.printDebugMessageLevel = max(rss_print.printDebugMessageLevel, 4)
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"')
    elif str(curSisend) != "":
        rss_print.print_debug(__file__, 'sisend: "' + curSisend + '"', 1)
        for j in range(0, len(RSSdefinitions)):
            if (curSisend == RSSdefinitions[j][1]):
                RSStoGenerate.append(j)
                break

if len(RSStoGenerate) < 1:
    rss_print.print_debug(__file__, "ei suutnud sisendist tuvastada sobivat nime, genereeritakse kõik vood.")
    RSStoGenerate = range(0, len(RSSdefinitions))

# make sure we have subfolders
if not os.path.exists(latestFeedsPath):
    os.makedirs(latestFeedsPath)
if not os.path.exists(oldersFeedsPath):
    os.makedirs(oldersFeedsPath)

# generate all feeds
for curRSS in RSStoGenerate:

    curParser = sys.modules['parser_' + RSSdefinitions[curRSS][0]]
    curName = RSSdefinitions[curRSS][1]
    curTitle = RSSdefinitions[curRSS][2]
    curDescription = RSSdefinitions[curRSS][2] + " - " + RSSdefinitions[curRSS][3]
    curDomain = curDomainRSS = RSSdefinitions[curRSS][4].replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')
    if len(RSSdefinitions[curRSS]) > 4 and len(RSSdefinitions[curRSS][5]) > 0:
        curDomainRSS = RSSdefinitions[curRSS][5]

    curFilename = curName + '.rss'
    curFilenameFull = latestFeedsPath + '/' + curFilename
    destFilenameFull = oldersFeedsPath + '/' + curFilename

    # load page into tree
    try:
        rss_print.print_debug(__file__, "pärime lehe: " + curDomainRSS, 2)
        pageHtmlTree = parsers_common.getArticleData(curDomainRSS, mainPage=True)
        rss_print.print_debug(__file__, parsers_common.elemtreeToString(pageHtmlTree), 4)
    except Exception as e:
        rss_print.print_debug(__file__, "Viga! Ei suutnud andmeid pärida leheküljelt: " + curDomainRSS)
        rss_print.print_debug(__file__, "Viga: " + str(e), 1)
        continue

    # get all content from page
    rss_print.print_debug(__file__, "parsime sisu: " + curDomainRSS, 2)
    dataset = curParser.getArticleListsFromHtml(pageHtmlTree, curDomain, maxArticleCount, getArticleBodies)
    rss_print.print_debug(__file__, dataset, 4)
    lastCountValue = 0
    for x in dataset:
        rss_print.print_debug(__file__, str(x) + "=", 3)
        rss_print.print_debug(__file__, dataset[x], 3)
        curCountValue = len(dataset[x])
        if (lastCountValue != 0 and curCountValue != 0 and lastCountValue != curCountValue):
            rss_print.print_debug(__file__, "'" + str(x) + "' leitud väärtuste arv: " + str(curCountValue) + " ei kattu eelmisega: " + str(lastCountValue), 0)
        else:
            rss_print.print_debug(__file__, "'" + str(x) + "' leitud väärtusi: " + str(curCountValue), 1)
        lastCountValue = curCountValue

    # combine rss file
    rss_print.print_debug(__file__, "koostame rss-i: " + curDomainRSS, 2)
    rss_content = rss_maker.rssmaker(dataset, curTitle, curDomain, curDomainRSS, curDescription)

    # move away old feed, if there is any
    try:
        os.rename(curFilenameFull, destFilenameFull)
        rss_print.print_debug(__file__, "faili liigutamine õnnestus: " + curFilenameFull + "->" + destFilenameFull, 1)
    except Exception as e:
        rss_print.print_debug(__file__, "faili liigutamine EBAõnnestus: " + curFilenameFull + "->" + destFilenameFull, 0)
        rss_print.print_debug(__file__, "Viga: " + str(e), 1)

    # write feed
    try:
        rss_content.write(open(curFilenameFull, 'wb'), encoding='UTF-8', pretty_print=True)
        rss_print.print_debug(__file__, "faili salvestamine õnnestus: " + curFilenameFull, 1)
    except Exception as e:
        rss_print.print_debug(__file__, "faili salvestamine EBAõnnestus: " + curFilenameFull, 0)
        rss_print.print_debug(__file__, "Viga: " + str(e), 1)

    # upload feed
    try:
        files = {rss_config.upload_name: open(curFilenameFull, 'rb')}
        reply = requests.post(rss_config.upload_url, files=files)

        rss_print.print_debug(__file__, "reply.status_code: " + str(reply.status_code), 2)
        if (reply.status_code is 200):
            rss_print.print_debug(__file__, "faili üleslaadimine õnnestus: " + curFilename, 1)
        else:
            rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + curFilename, 0)
            rss_print.print_debug(__file__, "Serveri vastus: " + str(reply.text), 1)
    except Exception as e:
        rss_print.print_debug(__file__, "faili üleslaadimine EBAõnnestus: " + curFilename, 0)
        rss_print.print_debug(__file__, "Viga: " + str(e), 1)
