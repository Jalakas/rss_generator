#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Tartu Ekspressi RSS-voo loomiseks
"""

from lxml import etree
from lxml import html
import makereq


def getArticleData(articleURL):
    """ Artikli lehe pärimine """
    aricleDataHtml = makereq.makeReq(articleURL)
    treeArt = html.fromstring(aricleDataHtml)
    return treeArt


def extractArticleHeader(tree):
    """ Artikli päise saamiseks """
    return next(iter(tree.xpath('//div[@class="full_width"]/p[1]/strong/text()') or []), None)


def extractArticleImage(tree):
    """ Artikli pildi aadressi saamiseks """
    return next(iter(tree.xpath('//div[@class="full_width"]/a/img[@class="thumb"]/@src') or []), None)
    
    
def extractArticleBody(tree):
    """ Artikli tervikteksti saamiseks """
    body = tree.xpath('//div[@class="full_width"]/p')
    fulltext = []
    for elem in body:
        rawtext = elem.text_content()
        try:
            rawtext = rawtext[:rawtext.index('Tweet\n')]
        except ValueError:
            None
        fulltext.append(rawtext)
    return ''.join(fulltext)
    

def getNewsList(newshtml,domain):
    """ Peameetod kõigi uudiste nimekirja loomiseks """
    tree = html.fromstring(newshtml)
    headLines = tree.xpath('//div[@class="forum"][2]/ul/li/a/text()')
    newsUrls = tree.xpath('//div[@class="forum"][2]/ul/li/a/@href')
    articleIds = []
    articleHeaders = []
    articleImages = []
    articleBodys = []
    newsUrls = [domain+elem for elem in newsUrls]
    #newsUrls = list(newsUrls[:1])
    #headLines = list(headLines[:1])

    for elem in newsUrls:
        articleIds.append(elem[elem.index('&id=')+4:elem.index('&',elem.index('&id=')+4)])
        articleTree = getArticleData(elem)
        
        articleHeaders.append(extractArticleHeader(articleTree))
        articleImages.append(extractArticleImage(articleTree))
        articleBodys.append(extractArticleBody(articleTree))

    return {"articleIds" : articleIds,
            "articleUrls" : newsUrls,
            "articleTitles" : headLines,
            "articleHeaders" : articleHeaders,
            "articleImages" : articleImages,
            "articleBodys" : articleBodys}
