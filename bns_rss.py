#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Lõunaeestlane RSS voo genereerimiseks veebilehelt
"""

import bns_parser
import makereq
import rssmaker

domain = 'http://bns.ee'
newshtml = makereq.makeReq(domain)

dataset = bns_parser.getNewsList(newshtml, domain)

rss = rssmaker.rssmaker(dataset, 'BNS', domain, 'BNS - Baltic News Service - uudised Eestist, Lätist, Leedust ja maailmast')

try:
    rss.write(open('bns.rss', 'wb'),
              encoding='UTF-8', pretty_print=True)
    print('Fail salvestatud')
except BaseException:
    print('Viga! - Ei õnnestunud faili salvestada!')
