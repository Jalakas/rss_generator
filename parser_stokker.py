#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Stokker Outlet RSS-voo sisendite parsimine
"""

import parsers_common


def getArticleListsFromHtml(pageTree, domain, maxPageURLstoVisit):
    """
    Meetod kõigi pakkumiste nimekirja loomiseks
    """

    articleDescriptions = []
    articleIds = []
    articleImages = pageTree.xpath('//div[@class="product_camp_box   w"]/a/div/div[@class="leftC"]/div/img/@src')
    articlePubDates = []
    articleTitles = pageTree.xpath('//div[@class="product_camp_box   w"]/a/div/div[@class="leftC"]/h3/text()')
    articleUrls = pageTree.xpath('//div[@class="product_camp_box   w"]/a/@href')
    articleUrls = parsers_common.domainUrls(domain, articleUrls)

    articleDescriptionsParents = pageTree.xpath('//div[@class="product_camp_box   w"]/a/div/div[@class="leftC"]')  # as a parent

    for i in range(0, len(articleUrls)):
        articleUrl = articleUrls[i]

        # get unique id from articleUrl
        articleIds.append(articleUrl.split('/')[-1].lstrip('-'))

        # description
        curArtDescParent = articleDescriptionsParents[i]
        curArtDescChilds = parsers_common.stringify_children(curArtDescParent)
        articleDescriptions.append(curArtDescChilds)

    return {"articleDescriptions": articleDescriptions,
            "articleIds": articleIds,
            "articleImages": articleImages,
            "articlePubDates": articlePubDates,
            "articleTitles": articleTitles,
            "articleUrls": articleUrls,
           }
