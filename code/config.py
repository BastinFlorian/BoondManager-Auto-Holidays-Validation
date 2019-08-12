# config.py

class Config(object):

    path_filenames = "../RENSEIGNEZ_MOI.txt"
    with open(path_filenames, "r") as f:
        t = f.readlines()
    x = []
    for lines in t:
        x.append(lines[lines.find('"') + 1:-(1 + lines[::-1].find('"'))])

    csv_attente = x[0]
    csv_validee = x[1]
    filename_source = x[2]
    filename_log = x[3]
    id_sheet = x[4]
    name_spreadsheet = x[5]
    filename_output_pypdf = x[6]
    filename_info_fiche_de_paie = x[7]
    filename_client_secret = x[8]
