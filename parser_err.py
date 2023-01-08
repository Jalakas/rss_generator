
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '/html/body/app-root/div/app-collection/div/div[2]/app-grid/div/div[1]/app-card/mat-card/a/div/img/@srcset')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '/html/body/app-root/div/app-collection/div/div[2]/app-grid/div/div[1]/app-card/mat-card/a/mat-card-title/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '/html/body/app-root/div/app-collection/div/div[2]/app-grid/div/div[1]/app-card/mat-card/a/@href')

    # video
    # remove unwanted content: titles
    dictFilters = (
        "2000.ee:",
        "AK filmikroonika 1958-1991:",
        "Ajalik ja ajatu",
        "Aktuaalne kaamera",
        "Eesti Gloobus",
        "Hommik Anuga:",
        "Insight",
        "Iseolemine:",
        "Johannese lähetamine",
        "Kes keda?",
        "Kodukäijad",
        "Koolitants",
        "Lasteekraan",
        "Lastetuba",
        "Laulge kaasa!",
        "Maahommik:",
        "Magus molekul:",
        "Meie kõrval:",
        "Mis teie kodus uudist?:",
        "Mis? Kus? Millal?:",
        "NOVA:",
        "Noor meister:",
        "Nädala intervjuu:",
        "OP:",
        "Oma tõde:",
        "Ongi Koik",
        "Osoon:",
        "Pea ees vette. Tai Kuningriigis:",
        "Pealtnägija:",
        "Peegel:",
        "Plekktrumm",
        "Prillitoos",
        "Püha päeva palvus:",
        "Rahvas laulab:",
        "Rakett 69:",
        "Reibas hommik",
        "Ringvaade",
        "Sinu uus sugulane:",
        "Suus sulav Eesti:",
        "TECHnolik",
        "TV 10 olümpiastarti",
        "Taevavalvurid",
        "Tanel ja kanad:",
        "Tarmo ja Aet liiguvad:",
        "Terevisioon:",
        "Tähendamisi",
        "Tähtede lava",
        "Ukraina stuudio:",
        "Välisilm:",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    # audio
    # remove unwanted content: titles
    dictFilters = (
        "AIATARK.",
        "DELTA.",
        "GOGOL.",
        "HARRI TIIDO TAUSTAJUTUD.",
        "HOMMIKUMÕTISKLUS.",
        "HUVITAJA.",
        "KIHNUKEELSED UUDISED",
        "KIRIKUELU.",
        "KULDRANDEVUU.",
        "LOETUD JA KIRJUTATUD.",
        "LUULERUUM.",
        "LUULETUS.",
        "MELOTURNIIR.",
        "MINITURNIIR.",
        "MNEMOTURNIIR",
        "MULGIKEELSED UUDISED",
        "MUST KLAHV, VALGE KLAHV.",
        "NAISTESAUN.",
        "OLUKORRAST RIIGIS",
        "PÄEVAKAJA",
        "RAHVA OMA KAITSE",
        "RAHVA TEENRID",
        "REPORTERITUND.",
        "SAMOST JA AASPÕLLU",
        "SETUKEELSED UUDISED",
        "SIILILEGI SELGE!",
        "SPORDIPÜHAPÄEV.",
        "TETRIS.",
        "UUDISED.",
        "VÕRUKEELSED UUDISED",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "titles")

    # remove unwanted content: descriptions
    dictFilters = (
        "vene keele",
        "venekeel",
    )
    articleDataDict = parsers_common.article_data_dict_clean(__file__, articleDataDict, dictFilters, "in", "descriptions")

    for i in parsers_common.article_urls_range(articleDataDict["urls"]):

        curArtPubImage = parsers_common.get(articleDataDict["images"], i, printWarning=0)
        if "url=" in curArtPubImage:
            curArtPubImages = curArtPubImage.split("url=")
            curArtPubImage = curArtPubImages[-1]
        articleDataDict["images"] = parsers_common.list_add_or_assign(articleDataDict["images"], i, curArtPubImage)

        if parsers_common.should_get_article_body(i):
            curArtUrl = parsers_common.get(articleDataDict["urls"], i)

            # load article into tree
            pageTree = parsers_common.get_article_tree(domain, curArtUrl, cache='cacheAll')

            # description
            curArtDesc = parsers_common.xpath_to("single", pageTree, '//div[@class="info-wrapper"]', parent=True)
            articleDataDict["descriptions"] = parsers_common.list_add_or_assign(articleDataDict["descriptions"], i, curArtDesc)

    return articleDataDict
