#!/usr/bin/env python3
# coding: utf-8



### Librairies ###
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import pandas as pd
import io
import datetime
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
from dateutil.relativedelta import relativedelta
import time


### function that merge two dict from values
## dict1 = {"a":[1,2],"b":[2,3]}
## dict2 = {"a":[3,4],"b":[2,3]}
## out = {"a":[1,2,3,4],"b":[2,3,2,3]}
def merge_dict(dict1, dict2):
    dict_merged = {}
    keys_dict1 = dict1.keys()
    keys_dict2 = dict2.keys()
    inter = [key for key in keys_dict1 if key in keys_dict2]
    for key in inter:
        print(key)
        dict_merged[key] = dict1[key]
        dict_merged[key].extend(dict2[key])
    exter_dict1 = [key for key in keys_dict1 if key not in inter]
    exter_dict2 = [key for key in keys_dict2 if key not in inter]
    for key in exter_dict1:
        dict_merged[key] = dict1[key]
    for key in exter_dict2:
        dict_merged[key] = dict2[key]
    return(dict_merged)


### Extract text from pdf using pdf miner###
def pdf2xt(path):
        rsrcmgr = PDFResourceManager()
        retstr = BytesIO()
        codec = 'utf-8'
        device = TextConverter(rsrcmgr, retstr, codec = codec)
        with open(path, "rb") as fp:  # open in 'rb' mode to read PDF bytes
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                for page in PDFPage.get_pages(fp, check_extractable=True):
                        interpreter.process_page(page)
                device.close()
                text = retstr.getvalue()
                retstr.close()
        return text


### Regex on extracted pdf to get cp N, cp N-1 & RTT
### and the name of each BeNexter
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
    
    #Solve pdf extraction problem with the following
    #techniques
    #Extracted value in the form "2.0810.58.4.22" to transform into 2.08, 10.58 and 4.22
    for nb in test[::-1]:
        decimale.append(nb[:2])
        entier.append(nb[2:])

    entier = entier[1:]
    for i in range(len(entier)):
        try :
            list_of_nb.append(float(entier[i]+'.'+decimale[i]))
        except ValueError:
            print("ERROR FUNCTION EXTRACTION_RTT_CONGES")
            #print(entier[i])
            #print(decimale[i])

    #Some pay slips do not contains taken CP and CP N-1
    #Deal with all the cases
    #To solve precision problems : 2.006 + 2.00 = 4.00600001 != 4.006
    #We add epsilon noise

    cmpt = 0

    # if RTT taken holidays for this month
    if (abs(list_of_nb[0] + list_of_nb[1] - list_of_nb[2]) < 0.001):

        RTT_solde, RTT_pris, RTT_acquis = list_of_nb[:3]
        cmpt = 3

    else:
        RTT_solde, RTT_acquis = list_of_nb[:2]
        cmpt = 2
    # if CP_N taken this month)

    if (abs(list_of_nb[cmpt] + list_of_nb[cmpt + 1] - list_of_nb[cmpt + 2]) < 0.001):

        Congé_N_solde, Congé_N_pris, Congé_N_acquis = list_of_nb[cmpt: cmpt + 3]
        cmpt += 3
    else:

        Congé_N_solde, Congé_N_acquis = list_of_nb[cmpt: cmpt + 2]
        cmpt += 2

    # if CP N-1 taken this month
    # if CP N-1 taken this month

    try:
        if ((abs(list_of_nb[cmpt] + list_of_nb[cmpt + 1] - list_of_nb[cmpt + 2]) < 0.001) and \
                 list_of_nb[cmpt]<(12*2.09)):

            Congé_N_1_solde, Congé_N_1_pris, Congé_N_1_acquis = list_of_nb[cmpt: cmpt + 3]

        else:

            if ((abs(list_of_nb[cmpt] - list_of_nb[cmpt + 1]) < 0.001) and list_of_nb[cmpt]<(12*2.09)):
                Congé_N_1_solde, Congé_N_1_acquis = list_of_nb[cmpt: cmpt + 2]

    except Exception as e:

        if ((abs(list_of_nb[cmpt] - list_of_nb[cmpt + 1]) < 0.001) and list_of_nb[cmpt]<(12*2.09)):
            Congé_N_1_solde, Congé_N_1_acquis = list_of_nb[cmpt: cmpt + 2]

    #print(list_of_nb)
    return [RTT_solde, RTT_pris, RTT_acquis, Congé_N_solde, Congé_N_pris,Congé_N_acquis,\
            Congé_N_1_solde, Congé_N_1_pris, Congé_N_1_acquis]
    

### Create a df with all the informations (cp, rtt, name) of the beNexteurs
def out(data):
    out = {}

    var = ["prenom","nom","RTT_solde","RTT_pris","RTT_acquis","Congé_N_solde","Congé_N_pris",\
           "Congé_N_acquis","Congé_N_1_solde","Congé_N_1_pris","Congé_N_1_acquis"]

    for name in var:
        out[name] = []

    # iterate on all BeNexteur
    #k = 0
    tmp = []
    for bulletin in data:

        u = 0
        # Split par espace pour récupérer la ligne de nombre qui nous intéresse (cette ligne contient le mot "Net",
        # du fait du scrapping 
        bulletin_splitted = bulletin.split()

        # Récupération du nom et prénom
        nom_prenom = bulletin_splitted[0].split("##")
        nom_compose = (len(nom_prenom) <= 3)
        if nom_compose:
                nom = nom_prenom[2]
                i = 0
                while (bulletin_splitted[1].split("##")[i].upper() ==
                       bulletin_splitted[1].split("##")[i]):
                        nom += ' ' + bulletin_splitted[1].split("##")[i]
                        i +=1
                        
                prenom = bulletin_splitted[1].split("##")[i]
        else:
                nom = nom_prenom[2]
                prenom = nom_prenom[3]

        rtt_pris = True 
        conge_n_pris = True
        for idx in range(len(bulletin_splitted)):
            sent = bulletin_splitted[idx]
            
            if(idx != len(bulletin_splitted)- 1):
                    sent_nxt = bulletin_splitted[idx+1]
            else :
                    sent_nxt = ""
            if ("Net" in sent and len(sent) > 22 and sent_nxt == "payé"):
                u += 1
                #("payé" == sent_nxt.strip()[:4])):
                # extraction des différents champs utils du pdf
                res = extraction_rtt_conges(sent[:-3].split("."))
                for i in range(len(res)):
                    # on vérifie que la valeur n'est pas au dessus du seuil maximale (résout pb de scraping)
                    cond = (res[i] < 2.08 * 13)
                    if (cond):
                        out[var[i+2]].append(res[i])
                    else:
                        print(nom)
                        print(res[i])
                        out[var[i + 2]].append(-1000)
                        print("ERROR IN THE FUNCTION OUT VALUES ARE TOO HIGH")

        if ((nom + prenom not in tmp) and u>0):
                tmp.append(nom + prenom)
                out["nom"].append(nom)
                out["prenom"].append(prenom)
    return(pd.DataFrame(out))


### RETRAIT DES CONGES DEMANDEES NE CORRESPONDANT NI A DES CP NI A DES RTT
def check_conge_exceptionel(attente, log_file, VALIDEE):

    # attente : fichiers.csv extracted from BoondManager with all the holidays
    # VALIDEE : TRUE is the holidays in "attente" have been validated and False ow
    dico_type_congé = {}
    problemes_type_conge = {}
    
    dico_type_congé["7"] = "Exceptionnelle"
    dico_type_congé["6"] = "Maladie sur justificatif"
    dico_type_congé["5"] = "Congé Sans Solde"
    if (not VALIDEE):

        exceptionnelle_conge = attente[~ attente["Code Absence"].isin([3,4])]
        for name in exceptionnelle_conge["NOM Prénom"].unique():

            if name in problemes_type_conge.keys():
                problemes_type_conge[name].append("\nPB CONGES: type de conges à traiter manuellement (exceptionnelle, maladie, sans solde)\n")
            else:
                problemes_type_conge[name] = ["\nPB CONGES: type de conges à traiter manuellement (exceptionnelle, maladie, sans solde)\n"]

    attente = attente[attente["Code Absence"].isin([3,4])]
    return(attente, problemes_type_conge)
    

###VERIFICATION DE LA DATE DE DEMANDE DE CONGES ( > AJD et < 120 jours) 
def check_conge_less_5_months(attente, log_file, VALIDEE):
    
    index_to_delete = []
    problemes_date = {}
    
    for i in attente.index:
        name = attente.loc[i, "NOM Prénom"]
        # select only the less than 5 months coming holidays
        date_of_today_plus_5months = date.today() + relativedelta(months=+4) 
        date_of_today_plus_5months.replace(day=1)
        sup_5months = attente.loc[i,"Début"] > pd.Timestamp(date_of_today_plus_5months)

        # CAS OU CONGES DEMANDEES ENCORE EN TRAITEMENT MAIS TROP LOINTAINES
        cond = sup_5months and not VALIDEE
        if cond:

            if(name in problemes_date.keys()):
                problemes_date[name].append("\nPB DATE 1. : la date de début est superieur "
                           "a 4 \n")
            else :
                problemes_date[name] = ["\nPB DATE 1. : la date de début est superieur "
                           "a 4 \n"]

            index_to_delete.append(i)
            
        # CAS OU CONGES DEMANDEES VALIDEES MAIS TROP LOINTAINES    
        cond = sup_5months and VALIDEE
        if cond :
            if (name in problemes_date.keys()):
                problemes_date[name].append("\nPB DATE 2. : vacances"
                          "validees dans plus de 4  mois non prises en compte dans les calculs")
            else:
                problemes_date[name] = ["\nPB DATE 2. : vacances"
                          "validees dans plus de 4 mois non prises en compte dans les calculs"]
            index_to_delete.append(i)
            
        # CAS OU CONGES DEMANDEES ENCORE EN TRAITEMENT MAIS TROP PASSEES
        cond = (int(str(attente.loc[i,"Début"] - pd.Timestamp.now()).split(" day")[0]) < 0)
        if cond:
            index_to_delete.append(i)

            if(not VALIDEE):

                if (name in problemes_date.keys()):
                    problemes_date[name].append("\nPB DATE 3. : date de demande de vacances deja passee \n")
                else:
                    problemes_date[name] = ["\nPB DATE 3. : date de demande de vacances deja passee \n"]

    attente = attente.drop(index_to_delete, axis = 0)
    return(attente, problemes_date)


### Create a dic of dataframe. The keys are the name of the BeNexters and the values are a df with 
### number of days for each type of holidays (dim1 (CP or RTT)) and for each month (dim 2)

def create_tab_to_insert_vacances_en_attente(attente, log_file, VALIDEE):
    
    actual_month = datetime.datetime.now().month
    column_name = [str((actual_month + i)%12) for i in range(5)]

    attente, problemes_type_conge = check_conge_exceptionel(attente, log_file, VALIDEE)
    attente.reset_index()
    attente, problemes_date = check_conge_less_5_months(attente, log_file, VALIDEE)
    
    attente.reset_index()
    
    names = attente["NOM Prénom"].unique()
    dict_out = {}
    
    
    for name in names:
        dict_out[name] = pd.DataFrame(data = np.zeros((2,5)), index = ['CP','RTT'] , columns = column_name)
    
    attente_cp = attente[attente["Code Absence"] == 3]
    for name in attente_cp["NOM Prénom"].unique():
        df_name = attente_cp[attente_cp["NOM Prénom"] == name]
        df_name = df_name.groupby(df_name['Début'].dt.strftime('%m'))['Durée'].sum().sort_values()
        for name_col in df_name.index:
            dict_out[name].loc["CP",str(int(name_col))] = df_name[name_col]
        
    attente_rtt = attente[attente["Code Absence"] == 4]
    for name in attente_rtt["NOM Prénom"].unique():
        df_name = attente_rtt[attente_rtt["NOM Prénom"] == name]
        df_name = df_name.groupby(df_name['Début'].dt.strftime('%m'))['Durée'].sum().sort_values()
        for name_col in df_name.index:
            dict_out[name].loc["RTT",str(int(name_col))] = df_name[name_col]
    
    return(dict_out, problemes_type_conge, problemes_date)


### Pipeline extracting csv from Bound and returning the dic of nb od days by month and type of holidays
def pipeline(csv_attente,log_file, VALIDEE):
    
    attente = pd.read_csv(csv_attente, sep =";")
    
    attente = attente.drop(["Référence de la ressource", "Matricule",\
                            "Type", "Date", "Nom Absence", "Fin"],axis = 1)

    attente["NOM Prénom"] = [' '.join(i) for i in zip(attente["Nom"].map(str),attente["Prénom"])]

    all_names_waiting_for_validation = attente["NOM Prénom"].unique()

    attente.Début = pd.to_datetime(attente.Début, dayfirst=True)
    attente.Durée = attente.Durée.astype(str).str.replace(',', '.').astype(float)

    out, problemes_type_conge, problemes_date = create_tab_to_insert_vacances_en_attente(attente, log_file, VALIDEE)
    return(out, all_names_waiting_for_validation, problemes_type_conge, problemes_date)
    

# Write in worksheet at the specific cells
def write_info_in_worksheet(info_paie, out_attente, out_valide, name, sh, problemes_date, problemes_type_conge):
    wks = sh.worksheet(name)

    cp_to_add = out_attente[name].loc["CP"].tolist()
    rtt_to_add = out_attente[name].loc["RTT"].tolist()

    #fill pbs in sheet
    pb_date_name = None
    pb_type_conge_name = None

    indice_row_pb_date = 8
    indice_col_pb_date = 9

    indice_row_pb_conge = 9
    indice_col_pb_conge = 9

    if (name in problemes_date.keys()):
        pb_date_name = problemes_date[name]

        try:
            wks.update_cell(indice_row_pb_date, indice_col_pb_date, " ".join(pb_date_name))
        except Exception as e :
            print("QUTOAS ERROR -- SLEEP 100 SEC")
            time.sleep(101)
            wks.update_cell(indice_row_pb_date, indice_col_pb_date, " ".join(pb_date_name))

    if (name in problemes_type_conge.keys()):
        pb_type_conge_name = problemes_type_conge[name]

        try:
            wks.update_cell(indice_row_pb_conge, indice_col_pb_conge, " ".join(pb_type_conge_name))
        except Exception as e :
            print("QUTOAS ERROR -- SLEEP 100 SEC")
            time.sleep(101)
            wks.update_cell(indice_row_pb_conge, indice_col_pb_date, " ".join(pb_type_conge_name))


    indice_col_cp = 2
    indice_col_rtt = 3

    indice_row_cp_rtt = 13
    indice_row_cp_rtt_validees= 12

    for (x,y) in zip(cp_to_add, rtt_to_add):
        indice_col_cp += 2
        indice_col_rtt += 2
        if(x + y == 0):
            continue
        try:
            wks.update_cell(indice_row_cp_rtt, indice_col_cp, x)
            wks.update_cell(indice_row_cp_rtt, indice_col_rtt, y)
        except Exception as e :
            print("QUTOAS ERROR -- SLEEP 100 SEC")
            time.sleep(101)
            wks.update_cell(indice_row_cp_rtt, indice_col_cp, x)
            wks.update_cell(indice_row_cp_rtt, indice_col_rtt, y)

    if name in out_valide.keys():
        cp_valide_to_add = out_valide[name].loc["CP"].tolist()
        rtt_valide_to_add = out_valide[name].loc["RTT"].tolist()
        indice_col_cp = 2
        indice_col_rtt = 3
        for (x,y) in zip(cp_valide_to_add, rtt_valide_to_add):
            indice_col_cp += 2
            indice_col_rtt += 2
            if (x + y == 0):
                continue
            try:
                wks.update_cell(indice_row_cp_rtt_validees, indice_col_cp, x)
                wks.update_cell(indice_row_cp_rtt_validees, indice_col_rtt, y)
            except Exception as e  :
                print("QUTOAS ERROR -- SLEEP 100 SEC")
                time.sleep(101)
                wks.update_cell(indice_row_cp_rtt_validees, indice_col_cp, x)
                wks.update_cell(indice_row_cp_rtt_validees, indice_col_rtt, y)

    df_name = info_paie[info_paie["NOM Prénom"] == name]
    if (df_name.empty):
        print("ERROR :  FICHE DE PAIE NOT FOUND FOR --- %s."%name)

    else:
        row_cp_n = 6
        row_cp_n1 = 7
        col_cp_n_n1 = 6
        row_rtt = 6
        col_rtt = 7

        try :
            wks.update_cell(row_cp_n, col_cp_n_n1, float(df_name["Congé_N_solde"]))
            wks.update_cell(row_cp_n1, col_cp_n_n1, float(df_name["Congé_N_1_solde"]))
            wks.update_cell(row_rtt, col_rtt, float(df_name["RTT_solde"]))
        except Exception  as e :
            print("QUTOAS ERROR -- SLEEP 100 SEC)")
            time.sleep(101)
            wks.update_cell(row_cp_n, col_cp_n_n1, float(df_name["Congé_N_solde"]))
            wks.update_cell(row_cp_n1, col_cp_n_n1, float(df_name["Congé_N_1_solde"]))
            wks.update_cell(row_rtt, col_rtt, float(df_name["RTT_solde"]))




####___________####
#
#       MAIN
#
####___________####



## PARAMETERS
def main():

    with open("./RENSEIGNEZ_MOI.txt", "r") as f:
        t = f.readlines()
    x =[]
    for lines in t:
        x.append(lines[lines.find('"')+1:-(1+lines[::-1].find('"'))])


    csv_attente = x[0]
    csv_validee = x[1]
    filename_source = x[2]
    filename_log = x[3]
    id_sheet = x[4]
    name_spreadsheet = x[5]
    filename_output_pypdf = x[6]
    filename_info_fiche_de_paie = x[7]
    filename_client_secret = x[8]


    ### MAIN EXTRACTION DEPUIS PDF
	### -------------------------- ###

    log_file = open(filename_log, "w")

    print('-- Extracting')
    pdf_text = pdf2xt(filename_source)
    #with open("output_true.txt","rb") as f:
    #    pdf_text = f.read()
            
    if filename_output_pypdf:
        print('-- Writing file')
        with open(filename_output_pypdf, "wb") as f:
            f.write(pdf_text)
        f = io.open(filename_output_pypdf, mode="r", encoding="utf-8")
    data = f.read()
    #data = pdf_text
    print('-- Files Written \n')
    df = out(str(data).split("##BULLETIN##")[1:])

    df["NOM Prénom"] = [' '.join(i) for i in zip(df["nom"].map(str),df["prenom"])]
    df.to_csv(filename_info_fiche_de_paie, index = None, header = True)

    ### MAIN EXTRACTION INFOS VACANCES
	### EN ATTENTE ET VALIDEES
	### -------------------------- ###
    print("-- Extracting info from Boond Manager csv")
    out_attente, all_names_waiting_for_validation,  pb_conge_attente, pb_date_attente  = \
        pipeline(csv_attente, log_file, VALIDEE = False)
    out_valide, _ , pb_conge_validee, pb_date_validee  = \
        pipeline(csv_validee, log_file, VALIDEE = True)

    pb_date = merge_dict(pb_date_attente, pb_date_validee)
    pb_conge = merge_dict(pb_conge_attente, pb_conge_validee)

    print("-- Extraction done\n")


    ### MAIN MODIFYING GOOGLE SHEETS
	### -------------------------- ###
    print("-- Creating & modifying worksheets")
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(filename_client_secret, scope)
    gc = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
	# Make sure you use the right name here

    sh = gc.open(name_spreadsheet)
    for name in out_attente.keys():
        try:
            sh.duplicate_sheet(source_sheet_id=id_sheet ,new_sheet_name=name)
            write_info_in_worksheet(df, out_attente, out_valide, name, sh, pb_date, pb_conge)
        except Exception as inst:
            if (str(inst).find("RESOURCE_EXHAUSTED")>-1):
                print ("resource exhausted...")
                time.sleep(101)
            print("Warning : worksheet already here, so worksheet replaced")
            try :
                worksheet_to_delete = sh.worksheet(name)
                sh.del_worksheet(worksheet_to_delete)
                sh.duplicate_sheet(source_sheet_id=id_sheet ,new_sheet_name=name)
            except Exception as e:
                time.sleep(101)
                worksheet_to_delete = sh.worksheet(name)
                sh.del_worksheet(worksheet_to_delete)
                sh.duplicate_sheet(source_sheet_id=id_sheet ,new_sheet_name=name)
            write_info_in_worksheet(df, out_attente, out_valide, name, sh, pb_date, pb_conge)


    # Deal with the case where the benexteur only take special holidays
    special_names = [name for name in all_names_waiting_for_validation if name not in out_attente.keys()]
    try:
        worksheet_to_delete = sh.worksheet("Infos supplémentaires")
        sh.del_worksheet(worksheet_to_delete)
        wks = sh.add_worksheet(title="Infos supplémentaires", rows=len(special_names), cols=10)
    except Exception as e:
        wks = sh.add_worksheet(title="Infos supplémentaires", rows=len(special_names), cols=10)

    for idx,name in enumerate(special_names):
        print(idx)
        value = name
        if name in pb_date.keys():
            value += " \n".join(pb_date[name])
        if name in pb_conge.keys():
            value += " \n".join(pb_conge[name])
        try:
            wks.update_cell(idx+1,1,value)
        except Exception as e:
            print("QUTOAS ERROR -- SLEEP 100 SEC")
            time.sleep(101)
            wks.update_cell(idx+1, 1, value)

    print("-- Modifications done")
		
	####___________####
	#
	#      END MAIN
	#
	####___________####
	
if __name__=='__main__':
	main()
