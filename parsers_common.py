#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Parserid erinevate lehtedega kasutamiseks
"""

import makereq
from lxml import html


def getArticleData(articleURL):
    """
    Artikli lehe pärimine
    """
    aricleDataHtml = makereq.makeReq(articleURL)
    treeArt = html.fromstring(aricleDataHtml)
    return treeArt


def treeExtract(tree, xpathValue):
    """
    Leiab etteantud artikli lehe puust etteantud xpathi väärtuse alusel objektid
    """
    return next(
        iter(
            tree.xpath(xpathValue) or []),
        None)
