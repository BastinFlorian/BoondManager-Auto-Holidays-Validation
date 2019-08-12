######
# Access, update and deletion of cell values
# Dealing with quotas error problems
######

# To understand quotas errors,
# see : https://developers.google.com/analytics/devguides/config/mgmt/v3/limits-quotas#mgmt_writes
import time


def acces_worksheet(sh, name):
    try:
        wks = sh.worksheet(name)
        return (wks)

    except Exception as inst:
        quotas_error = str(inst).find("RESOURCE_EXHAUSTED") > -1
        if (quotas_error):
            print("Waiting 100 sec from access worksheet")
            time.sleep(110)
            wks = acces_worksheet(sh, name)
            return (wks)

        else:
            # unknown error, reported
            print("%s does not exist".format(name))
            print(inst)
            raise NameError('PB acces_worksheet')


def delete_worksheet(sh, worksheet_to_delete):
    try:
        sh.del_worksheet(worksheet_to_delete)

    except Exception as inst:
        quotas_error = str(inst).find("RESOURCE_EXHAUSTED") > -1
        if (quotas_error):
            print("Waiting 100 sec from delete_worksheet")
            time.sleep(110)
            delete_worksheet(sh, worksheet_to_delete)

        else:
            # worksheet_to_delete does not exist
            print("%s does not exist so cannot be deleted".format(worksheet_to_delete))


def add_worksheet(sh, title, rows = 13, cols = 10):
    try:
        sh.add_worksheet(title=title, rows=rows, cols=cols)
    except Exception as inst:
        quotas_error = str(inst).find("RESOURCE_EXHAUSTED") > -1
        if (quotas_error):
            print("Waiting 100 sec from add_worksheet")
            time.sleep(110)
            add_worksheet(sh, title, rows, cols)

        elif (str(inst).find("INVALID_ARGUMENT") > -1):
            # worksheet already exist, then we overwrite
            worksheet_to_delete = acces_worksheet(sh, title)
            delete_worksheet(sh, worksheet_to_delete)
            add_worksheet(sh, title, rows, cols)

        else:
            # unknown error, reported
            print(inst)
            raise NameError('PB add_worksheet')


# Duplicate the type spreadsheet for each employee
def duplicate(sh, id_sheet, sheet_name):
    try:
        sh.duplicate_sheet(source_sheet_id=id_sheet, new_sheet_name=sheet_name)

    except Exception as inst:
        quotas_error = str(inst).find("RESOURCE_EXHAUSTED") > -1
        if (quotas_error):
            # Quotas error --
            print("Waiting 100 sec from duplicate")
            time.sleep(110)
            duplicate(sh, id_sheet, sheet_name)

        elif (str(inst).find("INVALID_ARGUMENT") > -1):
            # worksheet already exist, then we overwrite
            worksheet_to_delete = acces_worksheet(sh, sheet_name)
            delete_worksheet(sh, worksheet_to_delete)
            duplicate(sh, id_sheet, sheet_name)

        else:
            # unknown error, reported
            print(inst)
            raise NameError('PB duplicate')


def update_cell(wks, row, col, value):
    try:
        wks.update_cell(row, col, value)

    except Exception as inst:
        quotas_error = str(inst).find("RESOURCE_EXHAUSTED") > -1
        if (quotas_error):
            print("Waiting 100 sec from update cell")
            time.sleep(110)
            update_cell(wks, row, col, value)

        else:
            # unknown error, reported
            print(inst)
            raise NameError('PB update_cell')
