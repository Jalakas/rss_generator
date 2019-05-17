#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Stokker Outlet RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod kõigi pakkumiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleImages = parsers_common.xpath(pageTree, '//div[@class="product_camp_box   w"]/a/div/div[@class="leftC"]/div/img/@src')
    articlePubDates = []
    articleTitles = parsers_common.xpath(pageTree, '//div[@class="product_camp_box   w"]/a/div/div[@class="leftC"]/h3/text()')
    articleUrls = parsers_common.xpath(pageTree, '//div[@class="product_camp_box   w"]/a/@href')

    articleDescriptionsParents = parsers_common.xpath(pageTree, '//div[@class="product_camp_box   w"]/a/div/div[@class="leftC"]')  # as a parent
    articlePriceParents = parsers_common.xpath(pageTree, '//div[@class="product_camp_box   w"]/div[@class="priceCont"]')  # as a parent

    for i in range(0, min(len(articleUrls), maxArticleCount)):
        # description
        curArtDescParent = articleDescriptionsParents[i]
        curArtDescriptionsChilds = parsers_common.stringify_children(curArtDescParent)
        curArtPriceParent = articlePriceParents[i]
        curArtPriceChilds = parsers_common.stringify_children(curArtPriceParent)

        articleDescriptions.append(curArtDescriptionsChilds + "<br>" + curArtPriceChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
