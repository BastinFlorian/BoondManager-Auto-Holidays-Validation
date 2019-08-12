## PARAMETERS

from config import Config
import io
from extracting_from_payslip import *
from google_sheet_writing import *
from extracting_from_BM_csv import *

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():

    config = Config()

    log_file = open(config.filename_log, "w")
    #pdf_text = pdf2xt(config.filename_source)

    with open("output_true.txt", "rb") as f:
        pdf_text = f.read()

    if config.filename_output_pypdf:
        print('-- Writing file')
        with open(config.filename_output_pypdf, "wb") as f:
            f.write(pdf_text)
        f = io.open(config.filename_output_pypdf, mode="r", encoding="utf-8")
    data = f.read()
    # data = pdf_text
    print('-- Files Written \n')
    df = out(str(data).split("##BULLETIN##")[1:])

    df["NOM Prénom"] = [' '.join(i).replace("-", " ") for i in zip(df["nom"].map(str), df["prenom"])]
    df["NOM Prénom"] = df["NOM Prénom"].apply(lambda x: x.replace("-", " ").strip())

    df.to_csv(config.filename_info_fiche_de_paie, index=None, header=True)

    ### MAIN EXTRACTION INFOS VACANCES
    ### EN ATTENTE ET VALIDEES
    ### -------------------------- ###

    print("-- Extracting info from Boond Manager csv")
    out_attente, all_names_waiting_for_validation, pb_conge_attente, pb_date_attente = \
        pipeline(config.csv_attente, log_file, VALIDEE=False)
    out_valide, _, pb_conge_validee, pb_date_validee = \
        pipeline(config.csv_validee, log_file, VALIDEE=True)

    pb_date = merge_dict(pb_date_attente, pb_date_validee)
    pb_conge = merge_dict(pb_conge_attente, pb_conge_validee)

    print("-- Extraction done\n")

    ### MAIN MODIFYING GOOGLE SHEETS
    ### -------------------------- ###
    print("-- Creating & modifying worksheets")
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(config.filename_client_secret, scope)
    gc = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here

    sh = gc.open(config.name_spreadsheet)

    ## delete all previous sheets except congé paye and infos supplémentaires ##
    worksheet_list = sh.worksheets()

    for name in out_attente.keys():
        sheet_name = name
        duplicate(sh, config.id_sheet, sheet_name)
        write_info_in_worksheet(df, out_attente, out_valide, name, sh, pb_date, pb_conge)

    # Deal with the case where the benexteur only take special holidays
    special_names = [name for name in all_names_waiting_for_validation if name not in out_attente.keys()]
    wks = add_worksheet(sh, title="Infos supplémentaires", rows=13, cols=10)
    wks = acces_worksheet(sh, "Infos supplémentaires")
    col_idx = 1
    for idx, name in enumerate(special_names):
        if (idx > 13):
            col_idx += 5
            idx = 0
        value = name
        if name in pb_date.keys():
            value += " \n".join(pb_date[name])
        if name in pb_conge.keys():
            value += " \n".join(pb_conge[name])
        update_cell(wks, idx + 1, col_idx, value)

    print("-- Modifications done")


####___________####
#
#      END MAIN
#
####___________####

if __name__ == '__main__':
    main()
