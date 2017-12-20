#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HTML-i hankimine
"""

import requests


def makeReq(link):
    """
    Päringu teostamine HTML-i allalaadimiseks
    """
    headers = {
        'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0',
        'Accept-Encoding': 'gzip, deflate, compress'}
    session = requests.session()
    req = session.get(link, headers=headers)
    return req.content
