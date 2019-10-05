#!/usr/bin/env python3

"""
    Kettaoperatsioonid
"""

import gzip
import os
import stat
import pwd

import rss_config
import rss_print

FILE_ENCODING = "utf-8"


def get_url_string_from_cache(articleUrl):

    rss_print.print_debug(__file__, "kettalt hangitav leht: " + articleUrl, 2)

    osPath = os.path.dirname(os.path.abspath(__file__))
    osCacheFolder = osPath + '/' + 'article_cache'
    cacheArticleUrl = articleUrl.replace('/', '|')
    cacheDomainFolder = articleUrl.split('/')[2]
    osCacheFolderDomain = osCacheFolder + '/' + cacheDomainFolder
    osCacheFolderDomainArticle = osCacheFolderDomain + '/' + cacheArticleUrl

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

    htmlPageString = htmlPageBytes.decode(FILE_ENCODING)
    return htmlPageString


def rename_file(curFilenameFull, destFilenameFull):
    try:
        os.rename(curFilenameFull, destFilenameFull)
        rss_print.print_debug(__file__, "faili liigutamine õnnestus: " + curFilenameFull + "->" + destFilenameFull, 3)
    except Exception as e:
        rss_print.print_debug(__file__, "faili liigutamine EBAõnnestus: " + curFilenameFull + "->" + destFilenameFull, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)


def save_file(curFilenameFull, fileContent):
    try:
        fileContent.write(open(curFilenameFull, 'wb'), encoding=FILE_ENCODING, pretty_print=True)
        rss_print.print_debug(__file__, "faili salvestamine õnnestus: " + curFilenameFull, 3)
    except Exception as e:
        rss_print.print_debug(__file__, "faili salvestamine EBAõnnestus: " + curFilenameFull, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)


def set_user_as_file_owner(filePath):
    fileUid = os.stat(filePath)[stat.ST_UID]
    userUid = pwd.getpwnam(rss_config.LOCAL_USERNAME).pw_uid

    if userUid is None:
        rss_print.print_debug(__file__, "tundmatu süsteemikasutaja? (userUid=" + str(userUid) + ")", 0)
    elif fileUid == userUid:
        rss_print.print_debug(__file__, "süsteemi ja faili kasutajad langevad kokku (userUid=" + str(userUid) + ")==(" + str(fileUid) + "=fileUid)", 4)
    else:
        rss_print.print_debug(__file__, "süsteemi ja faili kasutajad ei lange kokku (userUid=" + str(userUid) + ")!=(" + str(fileUid) + "=fileUid)", 1)
        rss_print.print_debug(__file__, "proovime muuta omanikku (fileUid=" + str(fileUid) + "-> (userUid=" + str(userUid) + ") failil: " + filePath, 0)
        os.chown(filePath, int(userUid), int(userUid))


def write_file_as_gzip(filePath, htmlPageString):
    try:
        rss_print.print_debug(__file__, "asume salvestama kettale faili: " + filePath, 4)
        with gzip.open(filePath, 'wb') as cacheWriteFile:
            htmlPageBytes = bytes(htmlPageString, FILE_ENCODING)
            cacheWriteFile.write(htmlPageBytes)
            cacheWriteFile.close()
            set_user_as_file_owner(filePath)

            rss_print.print_debug(__file__, "fail õnnestus kettale salvestada: " + filePath, 3)
    except Exception as e:
        rss_print.print_debug(__file__, "faili ei õnnestunud kettale salvestada: " + filePath, 0)
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
