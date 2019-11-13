#!/usr/bin/env python3

"""
    Kettaoperatsioonid
"""

import gzip
import os
import pwd
import stat

import rss_config
import rss_print


def get_url_string_from_cache(articleUrl):

    rss_print.print_debug(__file__, "kettalt hangitav leht: " + articleUrl, 1)

    osPath = os.path.dirname(os.path.abspath(__file__))
    osCacheFolder = osPath + '/' + 'article_cache'
    cacheArticleUrl = articleUrl.replace('/', '|')
    cacheDomainFolder = articleUrl.split('/')[2]
    osCacheFolderDomain = osCacheFolder + '/' + cacheDomainFolder
    osCacheFolderDomainArticle = osCacheFolderDomain + '/' + cacheArticleUrl

    htmlPageString = read_file_string_from_disk(osCacheFolderDomainArticle)

    return htmlPageString


def read_file_string_from_disk(osCacheFolderDomainArticle):
    try:
        with gzip.open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
            htmlPageBytes = cacheReadFile.read()
    except Exception as e:
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 2)

        # pakitud faili ei leitud, proovime tavalist
        try:
            with open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
                htmlPageBytes = cacheReadFile.read()
        except Exception as e:
            rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 3)
            return ""

    try:
        htmlPageString = htmlPageBytes.decode(rss_config.FILE_ENCODING)
    except Exception as e:
        rss_print.print_debug(__file__, "kettalt loetud faili dekodeerimine utf-8 vorminguga EBAõnnestus", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        return ""

    return htmlPageString


def rename_file(filePath, filename):
    filePathFull = filePath + "/" + filename

    osPath = os.path.dirname(os.path.abspath(__file__))
    olderFeedsPath = osPath + '/' + 'older_feeds'
    if not os.path.exists(olderFeedsPath):
        os.makedirs(olderFeedsPath)
    destFilenameFull = olderFeedsPath + '/' + filename

    rss_print.print_debug(__file__, "asume liigutame faili: " + filePathFull + "->" + destFilenameFull, 3)
    try:
        os.rename(filePathFull, destFilenameFull)
        rss_print.print_debug(__file__, "faili liigutamine õnnestus: " + filePathFull + "->" + destFilenameFull, 3)
    except Exception as e:
        rss_print.print_debug(__file__, "faili liigutamine EBAõnnestus: " + filePathFull + "->" + destFilenameFull, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)


# ~ def rename_file(filePathFull, destFilenameFull):
    # ~ try:
        # ~ os.rename(filePathFull, destFilenameFull)
        # ~ rss_print.print_debug(__file__, "faili liigutamine õnnestus: " + filePathFull + "->" + destFilenameFull, 3)
    # ~ except Exception as e:
        # ~ rss_print.print_debug(__file__, "faili liigutamine EBAõnnestus: " + filePathFull + "->" + destFilenameFull, 0)
        # ~ rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)


def set_user_as_file_owner(filePathFull):

    fileUid = os.stat(filePathFull)[stat.ST_UID]
    userUid = pwd.getpwnam(rss_config.LOCAL_USERNAME).pw_uid

    if userUid is None:
        rss_print.print_debug(__file__, "tundmatu süsteemikasutaja? (userUid=" + str(userUid) + ")", 0)
    elif fileUid == userUid:
        rss_print.print_debug(__file__, "süsteemi ja faili kasutajad langevad kokku (userUid=" + str(userUid) + ")==(" + str(fileUid) + "=fileUid)", 4)
    else:
        rss_print.print_debug(__file__, "süsteemi ja faili kasutajad ei lange kokku (userUid=" + str(userUid) + ")!=(" + str(fileUid) + "=fileUid)", 1)
        rss_print.print_debug(__file__, "proovime muuta omanikku (fileUid=" + str(fileUid) + "-> (userUid=" + str(userUid) + ") failil: " + filePathFull, 0)
        os.chown(filePathFull, int(userUid), int(userUid))


def write_file(filePath, filename, htmlPageString):
    filePathFull = filePath + "/" + filename
    rss_print.print_debug(__file__, "asume salvestame kettale faili: " + filePathFull, 3)

    try:
        if isinstance(htmlPageString, str):
            with open(filePathFull, 'wb') as cacheWriteFile:
                htmlPageBytes = bytes(htmlPageString, rss_config.FILE_ENCODING)
                cacheWriteFile.write(htmlPageBytes)
                cacheWriteFile.close()
        else:
            htmlPageString.write(open(filePathFull, 'wb'), encoding=rss_config.FILE_ENCODING, pretty_print=True)
        rss_print.print_debug(__file__, "fail õnnestus kettale salvestada: " + filePathFull, 3)
    except Exception as e:
        rss_print.print_debug(__file__, "faili ei õnnestunud kettale salvestada: " + filePathFull, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)


def write_file_as_gzip(filePathFull, htmlPageString):
    rss_print.print_debug(__file__, "asume salvestama kettale faili: " + filePathFull, 3)
    try:
        if isinstance(htmlPageString, str):
            with gzip.open(filePathFull, 'wb') as cacheWriteFile:
                htmlPageBytes = bytes(htmlPageString, rss_config.FILE_ENCODING)
                cacheWriteFile.write(htmlPageBytes)
                cacheWriteFile.close()
        else:
            htmlPageString.write(gzip.open(filePathFull, 'wb'), encoding=rss_config.FILE_ENCODING, pretty_print=True)
        # set rights
        set_user_as_file_owner(filePathFull)
        rss_print.print_debug(__file__, "fail õnnestus kettale salvestada: " + filePathFull, 3)
    except Exception as e:
        rss_print.print_debug(__file__, "faili ei õnnestunud kettale salvestada: " + filePathFull, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)


def write_file_to_cache_folder(osCacheFolder, osCacheFolderDomain, osCacheFolderDomainArticle, htmlPageString):
    if not os.path.exists(osCacheFolder):
        rss_print.print_debug(__file__, "loome puuduva kausta: " + osCacheFolder, 0)
        os.makedirs(osCacheFolder)
    if not os.path.exists(osCacheFolderDomain):
        rss_print.print_debug(__file__, "loome puuduva kausta: " + osCacheFolderDomain, 0)
        os.makedirs(osCacheFolderDomain)

    write_file_as_gzip(osCacheFolderDomainArticle, htmlPageString)


def write_file_string_to_cache(articleUrl, htmlPageString):

    osPath = os.path.dirname(os.path.abspath(__file__))
    osCacheFolder = osPath + '/' + 'article_cache'
    cacheArticleUrl = articleUrl.replace('/', '|')
    cacheDomainFolder = articleUrl.split('/')[2]
    osCacheFolderDomain = osCacheFolder + '/' + cacheDomainFolder
    osCacheFolderDomainArticle = osCacheFolderDomain + '/' + cacheArticleUrl

    write_file_to_cache_folder(osCacheFolder, osCacheFolderDomain, osCacheFolderDomainArticle, htmlPageString)
