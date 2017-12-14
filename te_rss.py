#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Tartu Ekspressi RSS voo genereerimiseks veebilehelt
"""

import te_parser
import makereq
# import sys
import rssmaker

domain = 'http://tartuekspress.ee/'
newshtml = makereq.makeReq('http://tartuekspress.ee/index.php?page=20&type=3')

dataset = te_parser.getNewsList(newshtml, domain)

rss = rssmaker.rssmaker(dataset, 'Tartu Ekspress', 'http://tartuekspress.ee/?page=20&type=3', 'Tartu Ekspress - Kõik uudised')

try:
    rss.write(open('tartuekspress.rss', 'wb'),
              encoding='UTF-8', pretty_print=True)
    print('Fail salvestatud')
except BaseException:
    print('Viga! - Ei õnnestunud faili salvestada!')
