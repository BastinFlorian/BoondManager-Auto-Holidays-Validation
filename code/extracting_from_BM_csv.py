'''Dealing with Boond Manager .csv holidays files

Check the type of holidays -- check_conge_exceptionel(attente, log_file, VALIDEE)
Check the date of holidays -- check_conge_less_5_months(attente, log_file, VALIDEE)
Prepare data for processing -- create_tab_to_insert_vacances_en_attente(attente, log_file, VALIDEE)
Preprocess csv and apply above function -- pipeline(csv_attente, log_file, VALIDEE):
'''


import pandas as pd
import numpy as np
import datetime

from datetime import date
from dateutil.relativedelta import relativedelta

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
    return (dict_merged)


### RETRAIT DES CONGES DEMANDEES NE CORRESPONDANT NI A DES CP NI A DES RTT
def check_conge_exceptionel(attente, log_file, VALIDEE):
    # attente : fichiers.csv extracted from BoondManager with all the holidays
    # VALIDEE : TRUE is the holidays in "attente" have been validated and False ow

    problemes_type_conge = {}

    dico_type_congé = {}
    dico_type_congé["7"] = "Exceptionnelle"
    dico_type_congé["6"] = "Maladie sur justificatif"
    dico_type_congé["5"] = "Congé Sans Solde"
    if (not VALIDEE):
        exceptionnelle_conge = attente[~ attente["Code Absence"].isin([3, 4])]
        for name in exceptionnelle_conge["NOM Prénom"].unique():
            if name in problemes_type_conge.keys():
                problemes_type_conge[name].append(
                    "\nPB CONGES: type de conges à traiter manuellement (exceptionnelle, maladie, sans solde)\n")

            else:
                problemes_type_conge[name] = [
                    "\nPB CONGES: type de conges à traiter manuellement (exceptionnelle, maladie, sans solde)\n"]

    attente = attente[attente["Code Absence"].isin([3, 4])]

    return (attente, problemes_type_conge)


###VERIFICATION DE LA DATE DE DEMANDE DE CONGES ( > AJD et < 120 jours)
def check_conge_less_5_months(attente, log_file, VALIDEE):
    index_to_delete = []
    problemes_date = {}

    for i in attente.index:
        name = attente.loc[i, "NOM Prénom"]
        # select only the less than 5 months coming holidays
        date_of_today_plus_5months = date.today() + relativedelta(months=+4)
        date_of_today_plus_5months.replace(day=1)
        sup_5months = attente.loc[i, "Début"] > pd.Timestamp(date_of_today_plus_5months)

        # CAS OU CONGES DEMANDEES ENCORE EN TRAITEMENT MAIS TROP LOINTAINES
        cond = sup_5months and not VALIDEE
        if cond:
            if (name in problemes_date.keys()):
                problemes_date[name].append("\nPB DATE 1. : la date de début est superieur "
                                            "a 4 \n")
            else:
                problemes_date[name] = ["\nPB DATE 1. : la date de début est superieur "
                                        "a 4 \n"]
            index_to_delete.append(i)

        # CAS OU CONGES DEMANDEES VALIDEES MAIS TROP LOINTAINES
        cond = sup_5months and VALIDEE
        if cond:
            if (name in problemes_date.keys()):
                problemes_date[name].append("\nPB DATE 2. : vacances"
                                            "validees dans plus de 4  mois non prises en compte dans les calculs")
            else:
                problemes_date[name] = ["\nPB DATE 2. : vacances"
                                        "validees dans plus de 4 mois non prises en compte dans les calculs"]
            index_to_delete.append(i)

        # CAS OU CONGES DEMANDEES ENCORE EN TRAITEMENT MAIS TROP PASSEES
        cond = (pd.Timestamp.now() > attente.loc[i, "Début"] and \
                (pd.Timestamp.now().month != attente.loc[i, "Début"].month))
        if cond:
            index_to_delete.append(i)

            if (not VALIDEE):

                if (name in problemes_date.keys()):
                    problemes_date[name].append("\nPB DATE 3. : date de demande de vacances deja passee \n")
                else:
                    problemes_date[name] = ["\nPB DATE 3. : date de demande de vacances deja passee \n"]

    attente = attente.drop(index_to_delete, axis=0)
    return (attente, problemes_date)


### Create a dic of dataframe. The keys are the name of the BeNexters and the values are a df with
### number of days for each type of holidays (dim1 (CP or RTT)) and for each month (dim 2)
def create_tab_to_insert_vacances_en_attente(attente, log_file, VALIDEE):

    actual_month = datetime.datetime.now().month
    column_name = [str((actual_month + i) % 12) for i in range(5)]

    attente, problemes_type_conge = check_conge_exceptionel(attente, log_file, VALIDEE)
    attente.reset_index()

    attente, problemes_date = check_conge_less_5_months(attente, log_file, VALIDEE)
    attente.reset_index()

    names = attente["NOM Prénom"].unique()
    dict_out = {}

    for name in names:
        dict_out[name] = pd.DataFrame(data=np.zeros((2, 5)), index=['CP', 'RTT'], columns=column_name)

    attente_cp = attente[attente["Code Absence"] == 3]
    for name in attente_cp["NOM Prénom"].unique():
        df_name = attente_cp[attente_cp["NOM Prénom"] == name]
        df_name = df_name.groupby(df_name['Début'].dt.strftime('%m'))['Durée'].sum().sort_values()
        for name_col in df_name.index:
            dict_out[name].loc["CP", str(int(name_col))] = df_name[name_col]

    attente_rtt = attente[attente["Code Absence"] == 4]
    for name in attente_rtt["NOM Prénom"].unique():
        df_name = attente_rtt[attente_rtt["NOM Prénom"] == name]
        df_name = df_name.groupby(df_name['Début'].dt.strftime('%m'))['Durée'].sum().sort_values()
        for name_col in df_name.index:
            dict_out[name].loc["RTT", str(int(name_col))] = df_name[name_col]

    return (dict_out, problemes_type_conge, problemes_date)


### Pipeline extracting csv from Bound and returning the dic of nb od days by month and type of holidays
def pipeline(csv_attente,
             log_file,
             VALIDEE):

    attente = pd.read_csv(csv_attente, sep=";")
    attente = attente.drop(["Référence de la ressource", "Matricule",
                            "Type", "Date", "Nom Absence", "Fin"], axis=1)
    attente["NOM Prénom"] = [' '.join(i).replace("-", " ") for i in zip(attente["Nom"].map(str), attente["Prénom"])]
    attente["NOM Prénom"] = attente["NOM Prénom"].apply(lambda x: x.replace("-", " ").strip())

    all_names_waiting_for_validation = attente["NOM Prénom"].unique()
    attente.Début = pd.to_datetime(attente.Début, dayfirst=True)
    attente.Durée = attente.Durée.astype(str).str.replace(',', '.').astype(float)

    out, problemes_type_conge, problemes_date = create_tab_to_insert_vacances_en_attente(attente, log_file, VALIDEE)

    return (out, all_names_waiting_for_validation, problemes_type_conge, problemes_date)