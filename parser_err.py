
import parsers_common


def fill_article_dict(articleDataDict, pageTree, domain):

    articleDataDict["descriptions"] = parsers_common.xpath_to("list", pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]', parent=True)
    articleDataDict["images"] = parsers_common.xpath_to("list", pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/p[@class="img"]/a/img/@src')
    articleDataDict["titles"] = parsers_common.xpath_to("list", pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/text()')
    articleDataDict["urls"] = parsers_common.xpath_to("list", pageTree, '/html/body/div/div/div/div[@id="page"]/ul/li[@class="clear "]/div[@class="content"]/h2/a/@href')

    # video
    # remove unwanted content: titles
    dictList = [
        "2000.ee:",
        "AK filmikroonika 1958-1991:",
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
        "Meie kõrval:",
        "Mis teie kodus uudist?:",
        "Mis? Kus? Millal?:",
        "NOVA:",
        "Noor meister:",
        "Nädala intervjuu:",
        "OP:",
        "Oma tõde:",
        "Ongi Koik",
        "Pealtnägija",
        "Peegel:",
        "Plekktrumm",
        "Prillitoos:",
        "Püha päeva palvus:",
        "Rahvas laulab:",
        "Rakett 69:",
        "Reibas hommik",
        "Ringvaade",
        "Suus sulav Eesti:",
        "TECHnolik",
        "TV 10 olümpiastarti",
        "Taevavalvurid",
        "Tarmo ja Aet liiguvad:",
        "Terevisioon:",
        "Tähendamisi",
        "Tähtede lava",
        "Välisilm",
    ]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "titles")

    # remove unwanted content: description
    dictList = [
        "Johannes Tralla",
    ]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "descriptions")

    # audio
    # remove unwanted content: titles
    dictList = [
        "AIATARK.",
        "DELTA.",
        "GOGOL.",
        "HOMMIKUMÕTISKLUS.",
        "HUVITAJA.",
        "KIHNUKEELSED UUDISED",
        "KIRIKUELU.",
        "KITARRIMUUSIKAST JA -MÄNGIJAIST.",
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
        "SETUKEELSED UUDISED",
        "SIILILEGI SELGE!",
        "SPORDIPÜHAPÄEV.",
        "TETRIS.",
        "UUDISED.",
        "VÕRUKEELSED UUDISED",
        ]
    articleDataDict = parsers_common.article_data_dict_clean(articleDataDict, dictList, "in", "titles")

    return articleDataDict
