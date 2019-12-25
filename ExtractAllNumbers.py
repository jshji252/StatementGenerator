## The functions in this script are used to extract all the numbers
## in the excel file. It outputs the data as a Dictionary, with the
## Properties being the room numbers, like "0301" and "1213", and the
## key values being an instance of the Owner Class.

## For some Regex game
from re import findall

## This function takes in an openpyxl worksheet object and returns the room number
# Room number is always on the 10th row. This is currently the best approach.
# A more robus approach would be to search all the values and look for "Room # 0000" string,
# which will be computationally more work. Also, if this becomes necessary, it will be easy to implement.
# Thus, go for the 10th-row solution.
def ext_room_no(ws):
    row10 = ws[10]
    row10_vals = list()
    for cell in row10:
        row10_vals.append(cell.value)
    row10_vals = [item for item in row10_vals if item is not None]
    return findall("[0-9]+", row10_vals[0])[0]

## This function takes in an openpyxl worksheet object and returns the name of the owner
# Like the ext_room_no function, it is not super robust to go for the row number,
# but for the same reason stated above, it is a good choice for now.
def ext_owner_name(ws):
    row7 = ws[7]
    row7_vals = list()
    for cell in row7:
        row7_vals.append(cell.value)
    extraction = [item for item in row7_vals if item is not None]
    return findall(".+", extraction[1])[0]

## Change the format of the amounts for processing
# When the amounts are read from the excel sheet, they are
# string values, starting with the $ sign. Remove the $ sign,
# and also remove the comma which are sometimes present.
# Then outputs the numbers as a float rounded to the 2 decimal places.
def beautify_amount(value):
    if isinstance(value, str) and (value != ''):
        value = value[1:]
        value = value.replace(',','')
        return float('%.2f' % float(value))
    else:
        return value

## Checking the validity of the excel sheet
# The last sheet is sometimes a Blank page, not a statement.
# This function checks if it is a valid RMS statement or not.
def is_valid_statement(ws):
    # All valid RMS statements have the string below in B2.
    if ws["B2"].value == "Statement / Tax Invoice":
        return True
    else:
        print("There was an invalid RMS statement with the worksheet named " + ws.title + ".")
        return False

## Some sheets are the second page of the same statement. This second page is mostly useless.
# This function compares the 'room number' of each page and if two consecutive pages have the same room number,
# ditch the second page. After this 'censorship', this function returns the list of a sheet names
# which are to be processed.
def sheet_censoring(wb):
    ws_names = wb.sheetnames # This returns a list that contains the names of *all* the worksheets within the workbook.
    ws_names_valid = []
    for sheet in ws_names:
        if is_valid_statement(wb[sheet]):
            ws_names_valid.append(sheet)

    ws_names_censored = [] 
    i = 0
    length = len(ws_names_valid)
    #compare room numbers of two consecutive worksheets
    if length > 1:
        while i < (length-1):
            if (ext_owner_name(wb[ws_names_valid[i]]) == "Hotres Investments Pty Ltd"):
                i = i+1
            elif (ext_room_no(wb[ws_names_valid[i]]) != ext_room_no(wb[ws_names_valid[i+1]])):
                ws_names_censored.append(ws_names_valid[i])
                i = i+1
            else:
                ws_names_censored.append(ws_names_valid[i])
                i = i+2
    else:
        ws_names_censored = ws_names_valid

    #compare the last two spreadsheets
    if (ext_owner_name(wb[ws_names_valid[length-1]]) == "Hotres Investments Pty Ltd"):
        return ws_names_censored
    elif (ext_room_no(wb[ws_names_valid[length-1]]) != ext_room_no(wb[ws_names_valid[length-2]])):
        ws_names_censored.append(ws_names_valid[length-1])
        return ws_names_censored
    else:
        return ws_names_censored

## See if there was a Brought Forward from the previous month, in the 15th row.
def isBF(ws):
    row15 = ws[15]
    isBF = False
    BF = 0
    for cell in row15:
        if isinstance(cell.value, str) and (cell.value != ""):
            if(cell.value == "Brought Forward"):
                isBF = True
            if(cell.value[0] == '$'):
                BF = cell.value
    if isBF and BF:
        return beautify_amount(BF)
    else:
        return 0


## Extract the entire Totals table
def ext_totals(ws, is_init = False, self = None):
    #"TOTALS" will be written in column B, so find that column and note the Row number
    colB = ws['B']
    found = False
    for cell in colB:
        if isinstance(cell.value, str) and not(found):
            if(cell.value == "TOTALS"):
                rowTotals = cell.row
            elif (cell.value[:5] == "* All"):
                rowLE = cell.row
                found = True
            elif (cell.value[:6] == "Report"):
                rowLE = cell.row
                found = True
    rowFE = rowTotals+2 # The first entry of the summary table is two rows below TOTALS row
    rowFE_cells = ws[rowFE] # Make reference to all the Cells object in that FirstElement row.\
                            # With this, we'll find the colum numbers of entry name, Debit, Credit columns
    cols = list() # record the column numbers here
    for cell in rowFE_cells:
        if cell.value != None:
            cols.append(cell.column)
    rowCurrent = rowFE #Starting from the row of the first element, go through every second row
    totals = {} #and record the description, credit, debit amounts.
    incomes = {}
    while(rowCurrent < rowLE):
        if (ws.cell(row=rowCurrent, column=cols[0]).value != None):
            totals[ws.cell(row=rowCurrent, column=cols[0]).value] = {"Debit": beautify_amount(ws.cell(row = rowCurrent, column = cols[1]).value),\
                                                               "Credit": beautify_amount(ws.cell(row = rowCurrent, column = cols[2]).value)}
            if (ws.cell(row = rowCurrent, column = cols[2]).value != "$0.00") or (ws.cell(row=rowCurrent, column=cols[0]).value == "Gross Amount"):
                incomes[ws.cell(row=rowCurrent, column=cols[0]).value] = beautify_amount(ws.cell(row = rowCurrent, column = cols[2]).value)
        rowCurrent = rowCurrent+1 # Each element is 2 rows apart

    if(is_init):
        pass
        self.incomes = incomes
        self.grossIncome = float('%.2f' % (incomes["Gross Amount"] - isBF(ws)))
        self.broughtForward = isBF(ws)
        return totals

## Extract the entire Expenses part
def ext_expenses(ws):
    #"EXPENSES" will be written in column B, so find that column and note the Row number
    colB = ws['B']
    for cell in colB:
        if(cell.value == "EXPENSES"):
            rowExpenses = cell.row
    rowDescription = rowExpenses+1
    rowFE = rowDescription + 2
    cols = list()
    for cell in ws[rowDescription]:
        if cell.value != None:
            cols.append(cell.column)
    expenses = {}
    rowCurrent = rowFE
    while ws.cell(row=rowCurrent, column=cols[0]+1).value != None:
        expenses[ws.cell(row=rowCurrent, column=cols[0]+1).value] = beautify_amount(ws.cell(row=rowCurrent, column=cols[1]).value)
        rowCurrent = rowCurrent+1
    return expenses

## Extraact Income Expenses
# There are 4 different types of income expenses.
def ext_incomeExpenses(ws):
    row13 = ws[13]
    colB = ws['B']
    IEs = { "MgtFee": 0, "AdvFee": 0, "C/L/A": 0, "CCFee": 0}
    if ws["B12"].value == "INCOME":
        for cell in colB:
                if cell.value == "EXPENSES":
                    rowVals = cell.row - 2
        for cell in row13:
            for fee in IEs:
                if cell.value == fee:
                    if (ws.cell(row = rowVals, column = cell.column).value != None) and (ws.cell(row = rowVals, column = cell.column).value != ''):
                        IEs[fee] = beautify_amount(ws.cell(row = rowVals, column = cell.column).value)
                    else:
                        IEs[fee] = 0
    return IEs

## Extract each month
def ext_month(ws):
    row7 = ws[7]
    month = []
    for cell in row7:
        if cell.value != None:
            month.append(cell.value)
    month = month[2]
    return month

class Owner:
    def __init__(self, ws):
        self.name = ext_owner_name(ws)
        self.BF = isBF(ws)
        self.room = ext_room_no(ws)
        self.expenses = ext_expenses(ws)
        self.totals = ext_totals(ws, True, self)
        self.month = ext_month(ws)
        self.incomeExpenses = ext_incomeExpenses(ws)
##        self.incomes = incomes
##        self.grossIncome = self.incomes["Gross Amount"]


## All information will be extracted to the owners Dictionary,
# with each Property being the unit number and Key being an instance of Owner class.
# this function generates the Owner objects for all possible sheets
def create_dictionary(wb, owners, owners_list): #Create Dictionary for all owners
    ws_names = sheet_censoring(wb)
    for name in ws_names:
        if is_valid_statement(wb[name]):
            owners[ext_room_no(wb[name])] = Owner(wb[name])
    print("Here is the list of rooms ready in 'owners' dictionary:")
    for room_no in owners:
        print(room_no)
        owners_list.append(room_no)
