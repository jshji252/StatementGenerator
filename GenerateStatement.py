## This function takes in each Class instance as an input,
# and then generate php file for each owner.
# It performs several condition checks, for example, if the Net income is a negative value,
# then checks for Owner Receipts, to add to the statement. Similar checks are done for values like:
# Payment With Held, Net Amount Owing To Owner, etc.

from re import findall

def generate_statement(owner, chinese = True): 
    # these translation list will be used to translate english to chinese, in case (most cases)
    # chinese statements are needed. Which can be specified as the second parameter, which is set True for default
    expense_translation = [["ManagerLoan", "管理人贷款"],\
                       ["HotWaterCharges","热水及煤气费"],\
                       ["ElectricityCharges","电费"],\
                       ["PayTV","卫星电视费"],\
                       ["Internet","网络费"],\
                       ["PABXCharge","内部通讯费"],\
                       ["Postage","行政管理费用"],\
                       ["Repairs","维修费"],\
                       ["BodyCorporateLevy","法人团体费"],\
                       ["CouncilRates","市政费"],\
                       ["LandlordInsurance","保险费"],\
                       ["WaterCharges","污水管理费"],\
                       ["CarpetCleaning", "地毯养护费"],\
                       ["R", "其他费用"],\
                       ["ResNo", "其他费用"],\
                       ["ApartmentReplacements", "公寓设施替换"],\
                       ["SmokeAlarmSubscription", "烟雾警报器测试费(1年)"]
                       ]
    IE_translation = [["MgtFee", "出租管理费"],\
                ["AdvFee", "招租广告费"],\
                ["C/L/A", "清洁布草费"],\
                ["CCFee", "信用卡刷卡费"]]
    month_translation = [["Jan", "一月账单", "January Statment"], ["Feb", "二月账单", "February Statement"], ["Mar", "三月账单", "March Statement"],\
            ["Apr", "四月账单", "April Statement"], ["May", "五月账单", "May Statement"], ["Jun", "六月账单", "June Statement"],\
            ["Jul", "七月账单", "July Statement"], ["Aug", "八月账单", "August Statement"], ["Sep","九月账单", "September Statement"],\
            ["Oct", "十月账单", "October Statement"], ["Nov", "十一月账单", "November Statement"], ["Dec","十二月账单", "December Statement"]]

    ## Start working on the PHP creation.
    # Set the file name, etc.
    file_name = str(owner.room)+".php"
    output_html = open(file_name, 'w', encoding = 'UTF-8')

    ##PHP Structure Start part
    # The below main structure will be used and each placeholders will be
    # replaced appropriately.
    # ---- Start of the Main Structure ---- #
    main_structure_start = '''<?php
        include('../session.php');
        if ($login_session != **room_php**){
                header("location: ../index.php"); // Redirecting To Home Page
        } else {
                include('../login_count.php');
        }
        ?>
        <!DOCTYPE HTML>
        <html lang="zh">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title> ***Title*** </title>
        <link rel="stylesheet" type="text/css" href="../css/statement_style.css">
        </head>
        <body>
                <div class=container>
                        <!-- Header -->
                        <div class="header">
                                <img src="../logo/alcy_logo.jpg" alt="logo" height="64" width="64">
                                <h1>Alcyone</h1>
                                <div class="names">
***monthanddetails***
                                </div>
                        </div>
                        <!-- Title-->
                        <div class="statements">
                                <table>
                                        <tr>
                                                <th class="descriptions-heading">收支项目</td>
                                                <th class="amounts-heading">澳元$</td>
                                        </tr>
                                        <tr>
                                                <td class="descriptions-heading">租金毛收入</td>
                                                <td class="amounts-heading"> ***GrossIncome*** </td>
                                        </tr>

                                        <tr>
                                                <td class="descriptions-heading" onclick="funcIE()">出租费用<span class="small-font">明细</span></td>
                                                <td class="amounts-heading" onclick="funcIE()"> ***IncomeExpenses*** </td>
                                        </tr>
***IncomeExpensesSubTable***
                                        <tr>
                                                <td class="descriptions-heading" onclick="funcE()">其他支出<span class="small-font">明细</span></td>
                                                <td class="amounts-heading" onclick="funcE()"> ***Expenses*** </td>
                                        </tr>
***ExpensesSubTable***
                                        <tr>
                                                <td class="descriptions-heading">净收入</td>
                                                <td class="amounts-heading"> ***NetIncome*** </td>
                                        </tr>
***OwnerReceipts***
***PaymentWithheld***
***PaidToOwner***
***Outstanding***
***NettAmountOwingToOwner***
                                </table>
                        </div>
        '''

    # ---- End of the Main Structure ---- #
    main_structure_end = '''
                        <div class="footer">
                                <span onclick="logout()" id="logout">退出</span>
                                <hr style="border: 2px solid #626567;" />
                                <ol>
                                        <li>*此网站的目的在于方便业主查阅月账单，尽管在每次发布时，我们都会检查每笔金额，但若数据和您邮箱里收到的账单有出入，以正式电子账单为准。</li>
                                        <li>请点击“明细”查看账单详情。</li>
                                        <li>如果您想要查看您的另一套房产，请先登出当前界面。</li>
                                        <li>“其他费用”指非常规或特殊的费用。有疑问的话，请致信owners@alcyone.com.au获取更多信息。</li>
                                </ol>
                        </div>
                </div>
                <script>
                function funcE() {
                        var element = document.getElementsByClassName("E");
                        for (var i = 0; i < element.length; i++){
                                element[i].classList.toggle("donotdisplay");
                        }
                }

                function funcIE() {
                        var element = document.getElementsByClassName("IE");
                        for (var i = 0; i < element.length; i++){
                                element[i].classList.toggle("donotdisplay");
                        }
                }
                function logout() {
                        window.location.href = "../logout.php";
                }
                </script>
        </body>'''


    # Below String variables will be used to replace the placeholders in main_structure_start,
    # after appropriate processing.
    owner_receipts = '''                                        <tr>
                                                <td class="descriptions-heading">管理人贷款</td>
                                                <td class="amounts-heading"> ***OwnerReceipts*** </td>
                                        </tr>'''
    payment_withheld = '''                                        <tr>
                                                <td class="descriptions-heading">Payment Withheld</td>
                                                <td class="amounts-heading"> ***PaymentWithheld*** </td>
                                        </tr>'''
    Outstanding = '''                                        <tr>
                                                <td class="descriptions-heading">Outstanding</td>
                                                <td class="amounts-heading"> ***Outstanding*** </td>
                                        </tr>'''
    NAOTO = '''                                        <tr>
                                                <td class="descriptions-heading">Nett Amount Owing To Owner</td>
                                                <td class="amounts-heading"> ***NAOTO*** </td>
                                        </tr>'''
    paid_to_owner = '''                                        <tr>
                                                <td class="descriptions-heading">转账金额</td>
                                                <td class="amounts-heading"> ***PaidToOwner*** </td>
                                        </tr>'''
    paid_to_owner2 = '''                                        <tr>
                                                <td class="descriptions-heading">转账金额 (***name***)</td>
                                                <td class="amounts-heading"> ***PaidToOwner*** </td>
                                        </tr>'''
    month_and_roomno ='''                                        <p style="text-align: center; margin-bottom: 1rem;"> ***month*** </p>
                                        <p>单元号码 : ***roomno*** </p>'''

    ## Process month and room number details
    # replace placeholders in month_and_roomno
    
    for element in month_translation:
        if owner.month.find(element[0]) != -1:
            if chinese:
                thismonth = element[1]
            else:
                thismonth = element[2]

    month_and_roomno = month_and_roomno.replace("***month***", thismonth)
    month_and_roomno = month_and_roomno.replace("***roomno***", owner.room)
    # Replace the placeholder in the main structure.
    main_structure_start = main_structure_start.replace("***monthanddetails***", month_and_roomno)
    
    ## This is for the purpose of PHP session validation.
    # Get rid of the leading 0 if it is the case, because session names will be the room number in that format
    if(owner.room[0]=='0'):
            room_php = owner.room[1:]
    else:
            room_php = owner.room
    # Replace the placeholder in the main structure.
    main_structure_start = main_structure_start.replace("**room_php**", room_php)
    
    # Replace the page title in the header
    main_structure_start = main_structure_start.replace("***Title***", "Alcyone - " + str(room_php))

    # As many of the replacing values are float, create a simple helper replacer
    def replacer_helper(txt, replaceFrom, replaceTo):
        return txt.replace(replaceFrom, str(replaceTo))

    ## Replace Gross Income, Income Expenses, Expenses, Net Income placeholders with appropriate values
    # Simple calculations for expense and Net Income
    expense = owner.totals["Expenses"]["Debit"] + owner.totals["Brought Forward Expense"]["Debit"]
    netIncome = float('%.2f' % float(owner.grossIncome - owner.totals["Income Expenses"]["Debit"] - owner.totals["Expenses"]["Debit"]))

    main_structure_start = replacer_helper(main_structure_start, "***GrossIncome***", '%.2f' % owner.grossIncome)
    main_structure_start = replacer_helper(main_structure_start, "***IncomeExpenses***", '%.2f' % owner.totals["Income Expenses"]["Debit"])
    main_structure_start = replacer_helper(main_structure_start, "***Expenses***", '%.2f' % expense)
    main_structure_start = replacer_helper(main_structure_start, "***NetIncome***", '%.2f' % netIncome)

    ## IF THERE IS OWNER RECEIPTS (OR)
    # Then we need to add this to the PHP, to let the users know (that they have a debt now!)
    # Otherwise, get rid of the place holder by simply replacing it with ''
    if ("Owner Receipts" in owner.totals): # Making sure the property exists, because RMS isn't super reliable and if it doesn't exist the process will stop
        if (owner.totals["Owner Receipts"]["Credit"] > 0) and (netIncome < 0): # When there is Owner Receipts
            owner_receipts = replacer_helper(owner_receipts, "***OwnerReceipts***", '%.2f' % owner.totals["Owner Receipts"]["Credit"])
            main_structure_start = replacer_helper(main_structure_start, "***OwnerReceipts***", owner_receipts)
        else: #Generally, if Owner Receipts exists, then netIncome must be negative, and the Credit value of OR must be postiive.
            print("Owner Recetips exist, while net income is not negative. Something is wrong : ")
            print(owner.room)
            main_structure_start = replacer_helper(main_structure_start, "***OwnerReceipts***", "")
    else: # get rid of the placeholder, as OR doesn't exist
            main_structure_start = replacer_helper(main_structure_start, "***OwnerReceipts***", "")

    ## IF THERE IS PAYMENT WITHHELD (PW)
    # Then we need to add this to the PHP, to let the users know.
    # Otherwise, get rid of the place holder by simply replacing it with ''
    if ("Payment Withheld" in owner.totals): # Making sure the property exist
        if (owner.totals["Payment Withheld"]["Credit"]) > 0: #IF PW >0
            payment_withheld = replacer_helper(payment_withheld, "***PaymentWithheld***", '%.2f' % owner.totals["Payment Withheld"]["Credit"])
            main_structure_start = replacer_helper(main_structure_start, "***PaymentWithheld***", payment_withheld)
        else: #Otherwise, get rid of the place holder
            main_structure_start = replacer_helper(main_structure_start, "***PaymentWithheld***", "")
    else: #Otherwise, get rid of the place holder
            main_structure_start = replacer_helper(main_structure_start, "***PaymentWithheld***", "")

    ## IF THERE IS OUTSTANDING (OS)
    if ("Outstanding" in owner.totals): # Making sure the property exist
        if (owner.totals["Outstanding"]["Debit"]) > 0: #IF OS >0
            Outstanding = replacer_helper(Outstanding, "***Outstanding***", '%.2f' % owner.totals["Outstanding"]["Dedit"])
            main_structure_start = replacer_helper(main_structure_start, "***Outstanding***", Outstanding)
        else: #Otherwise, get rid of the placeholder
            main_structure_start = replacer_helper(main_structure_start, "***Outstanding***", "")
    else: #Otherwise, get rid of the placeholder
            main_structure_start = replacer_helper(main_structure_start, "***Outstanding***", "")

    ## IF THERE IS NET AMOUNT OWING TO OWNER (NAOTO) (rare case)
    # Then we need to add this to the PHP, to let the users know.
    # Otherwise, get rid of the place holder by simply replacing it with ''
    if ("Nett Amount Owing To Owner" in owner.totals): # Making sure the property exist
        if (owner.totals["Nett Amount Owing To Owner"]["Credit"]) > 0: #IF NAOTO >0
            NAOTO = replacer_helper(NAOTO, "***NAOTO***", '%.2f' % owner.totals["Nett Amount Owing To Owner"]["Credit"])
            main_structure_start = replacer_helper(main_structure_start, "***NettAmountOwingToOwner***", NAOTO)
        else: #Otherwise, get rid of the place holder
            main_structure_start = replacer_helper(main_structure_start, "***NettAmountOwingToOwner***", "")
    else: #Otherwise, get rid of the place holder
            main_structure_start = replacer_helper(main_structure_start, "***NettAmountOwingToOwner***", "")

    ## Sometimes multiple owners own apt, and want separte payment
    # Find the number of Paid to Owners by accessing the properties of TOTALS
    # and append each property to the list so that we can access the recipient's name later
    pto = []
    for prop in owner.totals:
        if prop[:4] == "Paid":
            pto.append(prop)
    
    if len(pto) == 1: # If there was only one recipient
        paid_to_owner = replacer_helper(paid_to_owner, "***PaidToOwner***", '%.2f' % owner.totals[pto[0]]["Debit"])
        main_structure_start = replacer_helper(main_structure_start, "***PaidToOwner***", paid_to_owner)
    elif len(pto) > 1: #If there was more than one recipient
        paid_to_owners = []
        for paid in pto: #Retrieve each recipient's name and create HTML element for each
            start_i = paid.rfind("-") + 2
            end_i = paid.rfind(" ")
            paid_to_owners.append(replacer_helper(replacer_helper(paid_to_owner2, "***name***", paid[start_i:end_i]), "***PaidToOwner***", '%.2f' % owner.totals[paid]["Debit"]))
        paid_to_owner_final = ''
        for paid in paid_to_owners: #Append the html elements so that it can be added to the main structure as one block
            paid_to_owner_final = paid_to_owner_final + paid
        main_structure_start = replacer_helper(main_structure_start, "***PaidToOwner***", paid_to_owner_final)

    ## There are two subtables to consider, IncomeExpenses and Expenses
    # This pre-created template will be modified aptly, then added to the sub-table
    subtable_expenses_temp='''<tr class="donotdisplay E">
                                            <td class="descriptions-content">&nbsp; ***ExpenseTitle*** </td>
                                            <td class="amounts-content"> ***ExpenseAmount*** &nbsp;</td>
                                        </tr>'''
    subtable_incomeexpenses_temp='''<tr class="donotdisplay IE">
                                            <td class="descriptions-content">&nbsp; ***ExpenseTitle*** </td>
                                            <td class="amounts-content"> ***ExpenseAmount*** &nbsp;</td>
                                        </tr>'''
    subtable_expenses = ''''''

    for expense in owner.expenses: # for each expense that was retrieved from the excel file, create a row
        if chinese:
                chn_title = findall("[a-zA-Z ]+", expense)[0]
                chn_title = chn_title.replace(' ','')
                for translation in expense_translation:
                        if translation[0] == chn_title:
                                chn_title = translation[1]
                expense_title = chn_title
        else:
                expense_title = expense
        current_expense = replacer_helper(subtable_expenses_temp, "***ExpenseTitle***", expense_title)
        current_expense = replacer_helper(current_expense, "***ExpenseAmount***", '%.2f' % owner.expenses[expense])
        subtable_expenses = subtable_expenses + current_expense
    
    if (owner.totals["Brought Forward Expense"]["Debit"] > 0) : # if there was BFE, then add this to the expense
        current_expense = replacer_helper(subtable_expenses_temp, "***ExpenseTitle***", "Brought Forward Expense")
        current_expense = replacer_helper(current_expense, "***ExpenseAmount***", '%.2f' % owner.totals["Brought Forward Expense"]["Debit"])
        subtable_expenses = subtable_expenses + current_expense
    main_structure_start = replacer_helper(main_structure_start, "***ExpensesSubTable***", subtable_expenses)
    
    subtable_incomeExpenses = ''''''
    for expense in owner.incomeExpenses: #for each income expense, create a row
        if chinese:
                chn_title = findall("[a-zA-Z /]+", expense)[0]
                chn_title = chn_title.replace(' ','')
                for translation in IE_translation:
                        if translation[0] == chn_title:
                                chn_title = translation[1]
                expense_title = chn_title
        else:
                expense_title = expense
        current_expense = replacer_helper(subtable_incomeexpenses_temp, "***ExpenseTitle***", expense_title)
        current_expense = replacer_helper(current_expense, "***ExpenseAmount***", '%.2f' % owner.incomeExpenses[expense])
        subtable_incomeExpenses = subtable_incomeExpenses + current_expense
    main_structure_start = replacer_helper(main_structure_start, "***IncomeExpensesSubTable***", subtable_incomeExpenses)


    ## Start Writing HTML file
    # Write the starting part
    output_html.write(main_structure_start)
    ## Write the ending part
    output_html.write(main_structure_end)
    ## Close and create the file
    output_html.close()

    ## Show successful execution to the shell
    print( "Export Success: Unit "+ owner.room + " - " + owner.name)
    return 0