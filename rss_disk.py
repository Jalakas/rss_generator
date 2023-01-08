
"""
    Kettaoperatsioonid.
"""

import gzip
import os
import pwd
import stat

import rss_config
import rss_print


def get_url_string_from_disk(articleUrl):
    rss_print.print_debug(__file__, "kettalt proovitav leht: " + articleUrl, 3)
    osPath = os.path.dirname(os.path.abspath(__file__))
    osCacheFolder = osPath + '/' + 'article_cache'
    cacheArticleUrl = articleUrl.replace('/', '|')
    cacheDomainFolder = articleUrl.split('/')[2]
    osCacheFolderDomain = osCacheFolder + '/' + cacheDomainFolder
    osCacheFolderDomainArticle = osCacheFolderDomain + '/' + cacheArticleUrl

    htmlPageString = read_file_string_from_disk(osCacheFolderDomainArticle)

    return htmlPageString


def move_file_to_old_folder(filePath, filename):
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


def read_file_string_from_disk(osCacheFolderDomainArticle):
    if not os.path.isfile(osCacheFolderDomainArticle):
        rss_print.print_debug(__file__, "kettal pole lugemiseks faili: " + osCacheFolderDomainArticle, 3)
        return ""

    try:
        with gzip.open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
            htmlPageBytes = cacheReadFile.read()
    except Exception as e:
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)

        # pakitud faili ei leitud, proovime tavalist
        try:
            with open(osCacheFolderDomainArticle, 'rb') as cacheReadFile:
                htmlPageBytes = cacheReadFile.read()
        except Exception as e:
            rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
            return ""

    try:
        htmlPageString = htmlPageBytes.decode(rss_config.CACHE_FILE_ENCODING)
    except Exception as e:
        rss_print.print_debug(__file__, "kettalt loetud faili dekodeerimine utf-8 vorminguga EBAõnnestus", 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        return ""

    return htmlPageString


def set_user_as_file_owner(filePathFull):

    fileUid = os.stat(filePathFull)[stat.ST_UID]
    userUid = pwd.getpwnam(rss_config.LOCAL_USERNAME).pw_uid

    if userUid is None:
        rss_print.print_debug(__file__, "tundmatu süsteemikasutaja? (userUid=" + str(userUid) + ")", 0)
    elif fileUid == userUid:
        rss_print.print_debug(__file__, "süsteemi ja faili kasutajad langevad kokku (userUid=" + str(userUid) + ")==(" + str(fileUid) + "=fileUid)", 4)
    else:
        rss_print.print_debug(__file__, "süsteemi ja faili kasutajad ei lange kokku (userUid=" + str(userUid) + ")!=(" + str(fileUid) + "=fileUid)", 1)
        try:
            rss_print.print_debug(__file__, "proovime omanikku muuta (fileUid=" + str(fileUid) + "-> (userUid=" + str(userUid) + ") failil: " + filePathFull, 0)
            os.chown(filePathFull, int(userUid), int(userUid))
        except Exception as e:
            rss_print.print_debug(__file__, "EBAõnnestus omaniku muutmine (fileUid=" + str(fileUid) + "-> (userUid=" + str(userUid) + ") failil: " + filePathFull, 0)
            rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)


def write_file(filePath, filename, htmlPageString, fileType=""):
    filePathFull = filePath + "/" + filename
    rss_print.print_debug(__file__, "asume salvestame kettale faili: " + filePathFull, 4)

    if fileType == "gzip":
        curFunction = gzip.open
    else:
        curFunction = open

    try:
        if isinstance(htmlPageString, str):
            with curFunction(filePathFull, 'wb') as cacheWriteFile:
                htmlPageBytes = bytes(htmlPageString, rss_config.CACHE_FILE_ENCODING)
                cacheWriteFile.write(htmlPageBytes)
                cacheWriteFile.close()
        else:
            htmlPageString.write(curFunction(filePathFull, 'wb'), encoding=rss_config.CACHE_FILE_ENCODING, pretty_print=True)
        # set rights
        set_user_as_file_owner(filePathFull)
        rss_print.print_debug(__file__, "fail õnnestus kettale salvestada: " + filePathFull, 4)
    except Exception as e:
        rss_print.print_debug(__file__, "faili ei õnnestunud kettale salvestada: " + filePathFull, 0)
        rss_print.print_debug(__file__, "exception = '" + str(e) + "'", 1)
        rss_print.print_debug(__file__, "e.errno = '" + str(e.errno) + "'", 1)  # pylint: disable=E1101

        if e.errno == 2:  # pylint: disable=E1101
            filePathFolderList = filePathFull.split("/")
            filePathFolder = "/".join(filePathFolderList[:-1])
            if not os.path.exists(filePathFolder):
                rss_print.print_debug(__file__, "loome puuduva kausta: " + filePathFolder, 0)
                os.makedirs(filePathFolder)
        elif e.errno == 13:  # pylint: disable=E1101
            set_user_as_file_owner(filePathFull)


def write_file_string_to_cache(articleUrl, htmlPageString):

    osPath = os.path.dirname(os.path.abspath(__file__))
    osCacheFolder = osPath + '/' + 'article_cache'
    cacheArticleUrl = articleUrl.replace('/', '|')
    cacheDomainFolder = articleUrl.split('/')[2]
    osCacheFolderDomain = osCacheFolder + '/' + cacheDomainFolder

    if not os.path.exists(osCacheFolder):
        rss_print.print_debug(__file__, "loome puuduva kausta: " + osCacheFolder, 0)
        os.makedirs(osCacheFolder)
        set_user_as_file_owner(osCacheFolder)
    if not os.path.exists(osCacheFolderDomain):
        rss_print.print_debug(__file__, "loome puuduva kausta: " + osCacheFolderDomain, 0)
        os.makedirs(osCacheFolderDomain)
        set_user_as_file_owner(osCacheFolderDomain)

    write_file(osCacheFolderDomain, cacheArticleUrl, htmlPageString, fileType="gzip")
