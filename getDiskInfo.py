import sys
import os
import subprocess
import xlsxwriter
import socket
import time
import paramiko
# pip install XlsxWriter
# pip install paramiko
# python getDiskInfo.py hosts.txt output.xlsx

row = 1

def parseData(cmdOut):
    myDict = {}
    if 'ERROR' in str(cmdOut):
        myDict["name"] = cmdOut.split()[0]
        myDict["path"] = 'ERROR'
        myDict["size"] = 'ERROR'
        myDict["used"] = 'ERROR'
    else:
        fields = cmdOut.split()
        myDict["name"] = fields[0]
        myDict["path"] = fields[1]
        myDict["size"] = fields[2]
        myDict["used"] = fields[3]
    return myDict

def createXLSX(name='output.xlsx'):
    wb = xlsxwriter.Workbook(name)
    return wb

def addSheet(wb,name = 'sheet 1'):
    ws = wb.add_worksheet(name)
    return ws

def writeInfo(info, sheet):
    global row
    sheet.write("A"+str(row),info["name"])
    sheet.write("B"+str(row),info["used"])
    sheet.write("C"+str(row),info["size"])

def closeXLSX(wb):
    wb.close()

def checkUsedSpace(serverPath,pathToLook='/'):
    #du -Ph -BG /var/ --max-depth=1 |sed '/^du/ d'| sort -h
    file1 = open(serverPath, 'r') 
    Lines = file1.readlines()
    file1.close()
    outCommands = []
    for srv in Lines:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())        
            srv = str(srv.replace(' ','').replace('\n',''))
            ssh.connect(hostname=srv, username='licontre', pkey=paramiko.RSAKey.from_private_key_file('aqui.pk'),timeout=6)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('''du -Ph -BG --max-depth=1 '''+str(pathToLook)+''' | sed '/^du/ d'| sort -h ''')
            mylines = ssh_stdout.readlines()
            print "---------------\t"+srv
            for li in mylines:
                print(li)
            print ssh_stderr
            print "---------------------------"
            ssh.close()
        except socket.error:
            mylines = ['ERROR']
            print "---------------\t"+srv
            print 'ERROR'
            print "---------------------------"
        outCommands.append(srv+' '+' '.join(mylines))
    file1.close()
    return outCommands

def checkFreeSpace(serverPath,pathToLook='/'):
    #df -BG -Ph path | sed '1d'
    file1 = open(serverPath, 'r') 
    Lines = file1.readlines()
    file1.close()
    outCommands = []
    for srv in Lines:
        try:
            ssh = paramiko.SSHClient()
            #ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())        
            srv = str(srv.replace(' ','').replace('\n',''))
            ssh.connect(hostname=srv, username='licontre', pkey=paramiko.RSAKey.from_private_key_file('aqui.pk'),timeout=6)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('''df -BG -Ph '''+str(pathToLook)+''' | sed '1d' ''')
            mylines = ssh_stdout.readlines()
            print "---------------\t"+srv
            for li in mylines:
                print(li)
            print ssh_stderr
            print "---------------------------"
            ssh.close()
        except socket.error:
            mylines = ['ERROR']
            print "---------------\t"+srv
            print 'ERROR'
            print "---------------------------"
        outCommands.append(srv+' '+' '.join(mylines))
    file1.close()
    return outCommands
    
def storeDataInXLSX(data,sheet):
    global row
    if row == 1 :
        sheet.write("A"+str(row),"SERVER")
        sheet.write("B"+str(row),"USED")
        sheet.write("C"+str(row),"SIZE")
    row = row + 1
    for el in data:
        out = parseData(el)
        writeInfo(out,sheet)
        row = row + 1

# Begining of the script
# Checking sent parameters
if sys.argv[1]== None:
 	raise
listOfCI = sys.argv[1]
xlsxFile = "testing.xlsx"
pathToLook = '/'

if len(sys.argv) > 2:
    xlsxFile = sys.argv[2]
# Arguments Checked
# Executing commands

#if len(sys.argv) == 3:
#check the number of parameter and if it is more than and create sheets due to them
myExcel = createXLSX(xlsxFile)
if len(sys.argv) < 3:
	outCmd = checkFreeSpace(listOfCI)
	sheetOne = addSheet(myExcel,"df root")
	storeDataInXLSX(outCmd,sheetOne)
else:
	for pth in range(3,len(sys.argv)):
		outCmd = checkFreeSpace(listOfCI,sys.argv[pth])
		sheet = addSheet(myExcel,"df "+str(sys.argv[pth]).replace('/','-'))
		storeDataInXLSX(outCmd,sheet)
		row = 1
closeXLSX(myExcel)
# END
