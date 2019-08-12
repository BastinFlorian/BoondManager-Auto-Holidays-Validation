'''Functions writing the needed informations in the google drive spreadsheet

From CP, RTT and holidays request : create a worksheet per employee --
write_info_in_worksheet(info_paie, out_attente, out_valide, name, sh, problemes_date, problemes_type_conge)

'''

from google_sheet_access import *

# Write in worksheet at the specific cells
def write_info_in_worksheet(info_paie, out_attente, out_valide, name, sh, problemes_date, problemes_type_conge):
    wks = acces_worksheet(sh, name)

    cp_to_add = out_attente[name].loc["CP"].tolist()
    rtt_to_add = out_attente[name].loc["RTT"].tolist()

    indice_row_pb_date = 8
    indice_col_pb_date = 9

    indice_row_pb_conge = 9
    indice_col_pb_conge = 9

    if (name in problemes_date.keys()):
        pb_date_name = problemes_date[name]
        update_cell(wks, indice_row_pb_date, indice_col_pb_date, " ".join(pb_date_name))

    if (name in problemes_type_conge.keys()):
        pb_type_conge_name = problemes_type_conge[name]
        update_cell(wks, indice_row_pb_conge, indice_col_pb_conge, " ".join(pb_type_conge_name))

    indice_col_cp = 2
    indice_col_rtt = 3

    indice_row_cp_rtt = 13
    indice_row_cp_rtt_validees = 12

    for (x, y) in zip(cp_to_add, rtt_to_add):
        indice_col_cp += 2
        indice_col_rtt += 2
        if (x + y == 0 or indice_col_rtt > 13):
            continue
        update_cell(wks, indice_row_cp_rtt, indice_col_cp, x)
        update_cell(wks, indice_row_cp_rtt, indice_col_rtt, y)

    if name in out_valide.keys():
        cp_valide_to_add = out_valide[name].loc["CP"].tolist()
        rtt_valide_to_add = out_valide[name].loc["RTT"].tolist()
        indice_col_cp = 2
        indice_col_rtt = 3
        for (x, y) in zip(cp_valide_to_add, rtt_valide_to_add):
            indice_col_cp += 2
            indice_col_rtt += 2
            if (x + y == 0):
                continue
            update_cell(wks, indice_row_cp_rtt_validees, indice_col_cp, x)
            update_cell(wks, indice_row_cp_rtt_validees, indice_col_rtt, y)

    df_name = info_paie[info_paie["NOM Prénom"] == name]
    if (df_name.empty):
        df_name = info_paie[info_paie["nom"].str.contains(name.upper().replace(" ", "|"), regex=True)]
        if len(df_name) != 1:
            df_name = info_paie[info_paie[info_paie["prenom"].apply(lambda x: x.lower()) \
                .str.contains(name.lower().replace(" ", "|"), regex=True)]]
            if len(df_name) != 1:
                df_name = info_paie[info_paie["NOM Prénom"] == name]

    if (df_name.empty):
        print("ERROR :  FICHE DE PAIE NOT FOUND FOR --- %s." % name)

    else:
        row_cp_n = 6
        row_cp_n1 = 7
        col_cp_n_n1 = 6
        row_rtt = 6
        col_rtt = 7

        update_cell(wks, row_cp_n, col_cp_n_n1, float(df_name["Congé_N_solde"]))
        update_cell(wks, row_cp_n1, col_cp_n_n1, float(df_name["Congé_N_1_solde"]))
        update_cell(wks, row_rtt, col_rtt, float(df_name["RTT_solde"]))
    print("%s done"%(name))
