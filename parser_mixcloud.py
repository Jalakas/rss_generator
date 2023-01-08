
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '//main/div[1]/div/div/div[1]/div/div', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '//main/div[1]/div/div/div[1]/div/div/a/div/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '//main/div[1]/div/div/div[1]/div/div/div/div[1]/div[2]/div[1]/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '//main/div[1]/div/div/div[1]/div/div/div/div[1]/div[2]/div[1]/a/@href')

    # remove unwanted content: titles
    dictFilters = (
        "(uus) raamat",
        "abramova",
        "akvavit",
        "annie ristiretk",
        "based broccoli",
        "beats of no nation",
        "bisweed",
        "ekkm",
        "error!",
        "floorshow",
        "gnoom",
        "hard feeler",
        "hillbilly picnic",
        "ida jutud",
        "ida räpp",
        "intro",
        "katus",
        "keskkonnatund",
        "kink konk",
        "korrosioon",
        "kräpp",
        "let me juke",
        "liin ",
        "liin",
        "lunchbreak lunchdate",
        "milk",
        "muster",
        "myös",
        "müürilehe hommik",
        "n-lib"
        "oleneb päevast!",
        "oujee!",
        "paneel",
        "playa music",
        "propel",
        "puhkus",
        "rets records",
        "room_202",
        "rõhk",
        "saal raadio",
        "soojad suhted",
        "svet nureka",
        "söökladisko",
        "triinemets",
        "vitamiin k",
        "zubrovka am",
        "ära kaaguta!",
        "öömaja",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    # remove unwanted content: descriptions
    dictFilters = (
        "#hip",
        "#rap",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "descriptions")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):
        # title
        curArtTitle = parsers_common.get(articleDataDict["titles"], i)
        curArtTitle = parsers_common.str_title_at_domain(curArtTitle, domain)
        articleDataDict["titles"] = parsers_common.list_add_or_assign(articleDataDict["titles"], i, curArtTitle)

    return articleDataDict
