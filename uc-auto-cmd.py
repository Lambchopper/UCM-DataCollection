#######################################
# UC-Auto-CMD is used to automate the
# the collection of data from the CLI
# of Cisco UC appliances.
# 
# Version 1.1
#######################################

#Backwards compatibility
from __future__ import print_function, unicode_literals, division

#import necessary modules
import paramiko
from paramiko_expect import SSHClientInteraction
import time, datetime
import getpass

#Output to Text File or Screen only
#strOutput = "s"
print("\n")
print("="*56)
print("Enter T to save as Text file, S for Screen Only")
print("="*56)
strOutput = input("T or S: ")
strOutput = strOutput.lower()
#Verify user entered input correctly
for i in range(1, 4):
     if i == 3:
          print("Incorrect Input, must be T or S")
          print("Failed too many times, terminating script")
          exit()
     if strOutput == "t" or strOutput == "s":
          break
     else:
          strOutput = input("T or S: ")
          strOutout = strOutput.lower()

#If we are going to save to file, collect date time for file name
if strOutput == "t":
     strDateTime = datetime.datetime.now().strftime("%I-%M-%p_%B-%d-%Y")

#Collect the command to run
print("\n")
print("="*56)
print("Enter the non-Interctive Command you'd like to run")
print("="*56)
strCommand = input("Command: ")

#Collect the file with the list of UC Nodes
print("\n")
print("="*56)
print("Enter the path and filename of the list of UC Nodes")
print("="*56)
strFile = input("File: ")
#Confirm file exists
try:
     with open(strFile) as f:
          listNodeList = f.read().splitlines()
except:
     print("\n")
     print("File with List of UC Nodes not found.")
     print("Please check your file and try again.")
     exit()

#Collect OS Admin Credentials
print("\n")
print("="*56)
print("Enter the OS Administrator credentials for this cluster")
print("="*56)
strUserID = input("User ID: ")
strPassword = getpass.getpass(prompt="Password: ")

#Meat and Potatoes
for strServer in listNodeList:
     #Connect to the node
     print("\n")
     print("="*56)
     print("Connecting to " + strServer)
     print("="*56)
     #Loop up to 3 times attempting to connect to the server
     #if an Authentication Failure occurs try again
     objSsh = paramiko.SSHClient()
     objSsh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
     for i in range(1, 4):
          try:
               objSsh.connect(strServer, username=strUserID, password=strPassword)
               strFail = "success"
          except paramiko.AuthenticationException:
               iTriesLeft = 3 - i
               if iTriesLeft == 0:
                    print("Authentication Failed Too Many Times")
                    print("Terminating Script")
                    objSsh.close()
                    exit()
               else:
                    strFail = "fail"
                    print("Authentication Failed")
                    print("You have " + str(iTriesLeft) + " tries left.")
                    strUserID = input("User ID: ")
                    strPassword = getpass.getpass(prompt="Password: ")
          except paramiko.SSHException as sshException:
               print("SSHException: " + sshException)
               objSsh.close()
               exit()
          except paramiko.socket.error as sshSocketErr:
               print("SSHSocketErr: " + sshSocketErr)
               objSsh.close()
               exit()
          except paramiko.BadHostKeyException as sshBadHostKey:
               print("BadHostKeyErr: " + sshBadHostKey)
               objSsh.close()
               exit()
          #Fail Flag used to decide if we need to break the loop
          #If we had a successful authentication, break the loop
          if strFail != "fail":
               break
          else:
               strFail = "reset"
     
     
     #Nowthat the SSH session is started, send the command to the UC Node
     #Use Expect because the UC CLI takes to long to start and commands
     #vary in duration of run time.  Expect admin: ensures we enter the
     #command at the appropriate time.
     objInteract = SSHClientInteraction(objSsh, timeout=60, display=False)
     objInteract.expect('admin:')
     objInteract.send(strCommand)
     objInteract.expect('admin:')
     strCmdResults = objInteract.current_output_clean
     objInteract.send('exit')
     objInteract.expect()
     objSsh.close()
     
     #Preent Results to Screen
     print("\n")
     print("="*56)
     print("Results of: " + strCommand)
     print("From Server: " + strServer)
     print("="*56)
     print(strCmdResults)

     #If user requested a text document, save the data to disk
     if strOutput == "t":
          print("Sending Result to Disk...")
          strFileName = "uc-command-" + strDateTime + ".txt"
          f = open(strFileName, mode="a")
          f.write("\n")
          f.write("="*56 + "\n")
          f.write("Results of: " + strCommand + "\n")
          f.write("From Server: " + strServer + "\n")
          f.write("="*56 + "\n")
          f.write(strCmdResults + "\n")
          f.close

#We are done and outta here!
exit()
