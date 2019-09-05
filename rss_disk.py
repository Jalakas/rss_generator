#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Kettaoperatsioonid
"""

import gzip
import os
import stat
import pwd

import rss_config
import rss_print


def set_user_as_file_owner(filePath):
    fileUid = os.stat(filePath)[stat.ST_UID]
    userUid = pwd.getpwnam(rss_config.LOCAL_USERNAME).pw_uid

    if userUid is None:
        rss_print.print_debug(__file__, "tundmatu süsteemikasutaja? (userUid=" + str(userUid) + ")", 0)
    elif(fileUid == userUid):
        rss_print.print_debug(__file__, "süsteemi ja faili kasutajad langevad kokku (userUid=" + str(userUid) + ")==(" + str(fileUid) + "=fileUid)", 2)
    else:
        rss_print.print_debug(__file__, "süsteemi ja faili kasutajad ei lange kokku (userUid=" + str(userUid) + ")!=(" + str(fileUid) + "=fileUid)", 1)
        rss_print.print_debug(__file__, "proovime muuta omanikku (fileUid=" + str(fileUid) + "-> (userUid=" + str(userUid) + ") failil: " + filePath, 0)
        os.chown(filePath, int(userUid), int(userUid))


def read_file_from_cache(osCacheFolderDomainArticle):
    try:
        with gzip.open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
            htmlPageBytes = cacheReadFile.read()
            return htmlPageBytes
    except Exception as e:
        rss_print.print_debug(__file__, "exception = " + str(e), 2)

        # pakitud faili ei leitud, proovime tavalist
        try:
            with open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
                htmlPageBytes = cacheReadFile.read()
                return htmlPageBytes
        except Exception as e:
            rss_print.print_debug(__file__, "exception = " + str(e), 3)
            return ""


def write_file_as_gzip(filePath, htmlPageBytes):
    try:
        rss_print.print_debug(__file__, "asume salvestama kettale faili: " + filePath, 4)
        with gzip.open(filePath, 'wb') as cacheWriteFile:
            cacheWriteFile.write(htmlPageBytes)
            cacheWriteFile.close()
            set_user_as_file_owner(filePath)
            rss_print.print_debug(__file__, "fail õnnestus kettale salvestada: " + filePath, 3)
    except Exception as e:
        rss_print.print_debug(__file__, "faili ei õnnestunud kettale salvestada: " + filePath, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)


def write_file_to_cache_folder(osCacheFolder, osCacheFolderDomain, osCacheFolderDomainArticle, htmlPageBytes):
    if not os.path.exists(osCacheFolder):
        rss_print.print_debug(__file__, "loome puuduva kausta: " + osCacheFolder, 0)
        os.makedirs(osCacheFolder)
    if not os.path.exists(osCacheFolderDomain):
        rss_print.print_debug(__file__, "loome puuduva kausta: " + osCacheFolderDomain, 0)
        os.makedirs(osCacheFolderDomain)

    write_file_as_gzip(osCacheFolderDomainArticle, htmlPageBytes)
