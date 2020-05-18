
'''Functions extracting the number of CP and RTT per employee

Extracting from pdf -- pdf2xt(path)
Selecting needed values and dealing with specific cases -- extraction_rtt_conges(test)
Creating a df with the selected informations per employee -- out(data)
'''


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import pandas as pd


# Extract text from pdf using pdf miner###
def pdf2xt(path):

    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    codec = 'utf-8'
    device = TextConverter(rsrcmgr, retstr, codec=codec)

    with open(path, "rb") as fp:  # open in 'rb' mode to read PDF bytes
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fp, check_extractable=True):
            interpreter.process_page(page)
        device.close()
        text = retstr.getvalue()
        retstr.close()

    return text


# Regex on extracted pdf to get cp N, cp N-1 & RTT
# and the name of each BeNexter
def extraction_rtt_conges(test):
    isinstance(test, list)

    RTT_solde = 0
    RTT_pris = 0
    RTT_acquis = 0
    Congé_N_solde = 0
    Congé_N_pris = 0
    Congé_N_acquis = 0
    Congé_N_1_solde = 0
    Congé_N_1_pris = 0
    Congé_N_1_acquis = 0

    list_of_nb = []
    decimale = []
    entier = []

    # Solve pdf extraction problem with the following
    # techniques
    # Extracted value in the form "2.0810.58.4.22" to transform into 2.08, 10.58 and 4.22
    for nb in test[::-1]:
        decimale.append(nb[:2])
        entier.append(nb[2:])

    entier = entier[1:]
    for i in range(len(entier)):
        try:
            list_of_nb.append(float(entier[i] + '.' + decimale[i]))

        except ValueError:
            print("ERROR FUNCTION EXTRACTION_RTT_CONGES")

    # Some pay slips do not contains taken CP and CP N-1
    # Deal with all the cases
    # To solve precision problems : 2.006 + 2.00 = 4.00600001 != 4.006
    # We add epsilon noise

    cmpt = 0

    # if RTT taken holidays for this month
    if abs(list_of_nb[0] + list_of_nb[1] - list_of_nb[2]) < 0.001:
        RTT_solde, RTT_pris, RTT_acquis = list_of_nb[:3]
        cmpt = 3

    else:
        RTT_solde, RTT_acquis = list_of_nb[:2]
        cmpt = 2
    # if CP_N taken this month)
    try:
        if (abs(list_of_nb[cmpt]
                + list_of_nb[cmpt + 1]
                - list_of_nb[cmpt + 2]) < 0.001):
            Congé_N_solde, Congé_N_pris, Congé_N_acquis = list_of_nb[cmpt: cmpt + 3]
            cmpt += 3

        else:
            Congé_N_solde, Congé_N_acquis = list_of_nb[cmpt: cmpt + 2]
            cmpt += 2

    except IndexError:
        print(list_of_nb)

    # if CP N-1 taken this month
    print(cmpt)
    try:
        if ((abs(list_of_nb[cmpt] + list_of_nb[cmpt + 1] - list_of_nb[cmpt + 2]) < 0.001)):
            Congé_N_1_solde, Congé_N_1_pris, Congé_N_1_acquis = list_of_nb[cmpt: cmpt + 3]

        else:
            if ((abs(list_of_nb[cmpt] - list_of_nb[cmpt + 1]) < 0.001)):
                Congé_N_1_solde, Congé_N_1_acquis = list_of_nb[cmpt: cmpt + 2]

    except Exception as e:
        try:
            if ((abs(list_of_nb[cmpt] - list_of_nb[cmpt + 1]) < 0.001)):
                Congé_N_1_solde, Congé_N_1_acquis = list_of_nb[cmpt: cmpt + 2]
        except Exception as e:
            Congé_N_1_solde, Congé_N_1_acquis = 0, 0

    if (Congé_N_pris > 0.001):
        Congé_N_1_pris = Congé_N_1_solde
        Congé_N_1_solde = 0
    print([RTT_solde, RTT_pris, RTT_acquis, Congé_N_solde, Congé_N_pris, Congé_N_acquis, \
            Congé_N_1_solde, Congé_N_1_pris, Congé_N_1_acquis])
    return [RTT_solde, RTT_pris, RTT_acquis, Congé_N_solde, Congé_N_pris, Congé_N_acquis, \
            Congé_N_1_solde, Congé_N_1_pris, Congé_N_1_acquis]


### Create a df with all the informations (cp, rtt, name) of the beNexteurs
def out(data):

    out = {}
    var = ["prenom", "nom", "RTT_solde", "RTT_pris", "RTT_acquis", "Congé_N_solde", "Congé_N_pris", \
           "Congé_N_acquis", "Congé_N_1_solde", "Congé_N_1_pris", "Congé_N_1_acquis"]

    for name in var:
        out[name] = []

    # iterate on all BeNexteur
    tmp = []
    for bulletin in data:

        u = 0
        # Split par espace pour récupérer la ligne de nombre qui nous intéresse (cette ligne contient le mot "Net",
        # du fait du scrapping
        bulletin_splitted = bulletin.split()

        # Get name and surname
        nom_prenom = bulletin_splitted[0].split("##")
        nom_compose = (len(nom_prenom) <= 3)
        if nom_compose:
            nom = nom_prenom[2]
            i = 0
            while (bulletin_splitted[1].split("##")[i].upper() ==
                   bulletin_splitted[1].split("##")[i]):
                nom += ' ' + bulletin_splitted[1].split("##")[i]
                i += 1

            prenom = bulletin_splitted[1].split("##")[i]
            i += 1
            if (bulletin_splitted[2].split("##")[0] != "Eléments"):
                prenom += ' ' + bulletin_splitted[2].split("##")[0]

        else:
            nom = nom_prenom[2]
            prenom = nom_prenom[3]
            if (bulletin_splitted[1].split("##")[0] != "Eléments"):
                prenom += ' ' + bulletin_splitted[1].split("##")[0]

        rtt_pris = True
        conge_n_pris = True

        for idx in range(len(bulletin_splitted)):
            sent = bulletin_splitted[idx]
            if (idx != len(bulletin_splitted) - 1):
                sent_nxt = bulletin_splitted[idx + 1]

            else:
                sent_nxt = ""

            if ("Net" in sent and len(sent) > 22 and sent_nxt == "payé"):
                u += 1
                # ("payé" == sent_nxt.strip()[:4])):
                # extraction des différents champs utils du pdf
                res = extraction_rtt_conges(sent[:-3].split("."))
                for i in range(len(res)):
                    # on vérifie que la valeur n'est pas au dessus du seuil maximale (résout pb de scraping)
                    ##  A CHANGER DANS L HYPOTHESE OU IL EST POSSIBLE D AVOIR PLUS DE
                    ## 35 JOURS DE CP SUR UNE ANNEE
                    cond = (res[i] < 35)
                    if (cond):
                        out[var[i + 2]].append(res[i])

                    else:
                        out[var[i + 2]].append(0)

        if ((nom + prenom not in tmp) and u > 0):
            tmp.append(nom + prenom)
            out["nom"].append(nom.replace("-", " "))
            out["prenom"].append(prenom.replace("-", " "))

    out = pd.DataFrame(out)

    return (out)

