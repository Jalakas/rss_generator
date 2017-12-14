#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Kuma RSS voo genereerimiseks veebilehelt
"""

import kuma_parser
import makereq
# import sys
import rssmaker

domain = 'http://kuma.fm/'
newshtml = makereq.makeReq(domain)

dataset = kuma_parser.getNewsList(newshtml, domain)

rss = rssmaker.rssmaker(dataset, 'Kuma', domain, 'Kuma - Kõik uudised')

try:
    rss.write(open('kuma.rss', 'wb'),
              encoding='UTF-8', pretty_print=True)
    print('Fail salvestatud')
except BaseException:
    print('Viga! - Ei õnnestunud faili salvestada!')
