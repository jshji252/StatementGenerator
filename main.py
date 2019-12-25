## Import Functions
from ExtractAllNumbers import create_dictionary
from GenerateStatement import generate_statement
##Load modules
from random import randint
from openpyxl import load_workbook

# Using the openpyxl module, load the workbook as an openpyxl object
origin_wb = load_workbook(filename="../original_statements_excel/Owner_Statement_11.xlsx")

## Create the dictionary that contains necessary numbers for all owners
owners = {}
owners_list = []
create_dictionary(origin_wb, owners, owners_list)
# Now the data is available in 'owners' dictinoary

## This is a simple functino used to create the PHP files for all owners
def gas():
        for i in owners:
                generate_statement(owners[i])
#                generate_statement(owners[i], False) #for english
        pass
gas()



## Currently the password is created by the admin (me) and sent out to the owners
# The below functions is used to create necessary SQL statement to add randomly
# generated passwords to the db, and also for messaging the owners

def construct_query(ws, printsql, printmsg, printnames):
    def replace_3times(template, first='', second='', third = ''):
        a = template.replace("*1*", first)
        a = a.replace("*2*", second)
        a = a.replace("*3*", third)
        return a
        
    ## Unit number, password, statementaddress
    output = []
    for i in ws:
        output.append([i[3],\
                       randint(99999, 999999),\
                       "./statements/"+i[3]+".php",\
                       i[2]])
    for j in range(len(output)):
        if output[j][0][0] == "0":
            output[j][0] = output[j][0][1:]
    sql_template = "INSERT INTO `owners`(`username`, `password`, `statement`) VALUES (*1*,*2*,*3*);"
    msg_template = '''您好，
为了给您提供更好地服务，我们对帐单系统进行了升级。本月的账单请您用以下用户名及密码登录 www.ch-alcyone.com 进行查看，您的用户名是 *1*，密码是 *2*。如有任何问题，请联系我们。
谢谢。'''
    sql_output = []
    msg_output = []
    names_template = '''UPDATE `owners` SET `owner_name`=*1* WHERE `username` = *2*;'''
    names_output = []
    for j in range(len(output)):
        sql_output.append(replace_3times(sql_template, output[j][0], str(output[j][1]),'"'+output[j][2]+'"'))
        msg_output.append(replace_3times(msg_template, output[j][0], str(output[j][1])))
        names_output.append(replace_3times(names_template, '"'+output[j][3]+'"', output[j][0]))

    if printsql:
        print("SQL_OUTPUT")
        for i in sql_output:
                print(i)
    if printmsg:
        print("Message_OUTPUT")
        for i in msg_output:
                print(i)
    if printnames:
        print("names_OUTPUT")
        for i in names_output:
            print(i)
    return [sql_output, msg_output, names_output]
