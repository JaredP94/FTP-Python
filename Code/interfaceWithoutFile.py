import os
import socket
import sys
import time
from os import walk
from pathlib import Path
from time import sleep
import mimetypes

import magic
from PyQt4 import QtGui
from PyQt4.QtCore import QDir, Qt
from PyQt4.QtGui import (QApplication, QColumnView, QFileSystemModel,
                         QSplitter, QTreeView)

styleSheet = """
QTreeView {
    alternate-background-color: #FFFFFF;
    background: #F5F5F5;
}
QTreeView::item:selected {
     background-color: #1d3dec;
     color: white;
}
"""

binary_buffer = 4194304

class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):      
        style = QApplication.style()

        self.path = str(Path.home())
        self.filePath = str(Path.home())
        self.file_all = style.standardIcon(QtGui.QStyle.SP_FileIcon)
        self.dir_all = style.standardIcon(QtGui.QStyle.SP_DirIcon)
        self.setStyleSheet(styleSheet)
        self.password=''
        self.username=''
        self.newDir = ''

        # Create grid
        grid = QtGui.QGridLayout()
        grid.setSpacing(10) 

        # Create buttons
        download = QtGui.QPushButton("Download")
        upload = QtGui.QPushButton("Upload")
        upload.clicked.connect(self.defineFileType)
        download.clicked.connect(self.defineDownloadType)
        connectToServer = QtGui.QPushButton("Connect")
        connectToServer.clicked.connect(self.connect_to_server)
        disconnectFromServer = QtGui.QPushButton("Disconnect")
        disconnectFromServer.clicked.connect(self.disconnect_from_server)
        makeDirectory = QtGui.QPushButton("Create Directory")
        makeDirectory.clicked.connect(self.mkdir)
        delete = QtGui.QPushButton("Delete")
        delete.clicked.connect(self.deleteDir)

        # Create text boxes and labels
        ip=QtGui.QLabel("IP Address")
        self.ipAddress = QtGui.QLineEdit()
        self.ipAddress.setFixedWidth(150)

        portLabel=QtGui.QLabel("Port")
        self.port = QtGui.QLineEdit()
        self.port.setFixedWidth(150)

        userName=QtGui.QLabel("Username")
        self.name = QtGui.QLineEdit()
        self.name.setFixedWidth(150)
	
        password1=QtGui.QLabel("Password")
        self.password = QtGui.QLineEdit()
        self.password.setFixedWidth(150)
        self.password.setEchoMode(QtGui.QLineEdit.Password)

        # Add widgets to grid
        grid.addWidget(ip, 0,0,1,1)
        grid.addWidget(self.ipAddress, 0,1,1,2)
        grid.addWidget(portLabel, 0,3,1,1)
        grid.addWidget(self.port,0,4,1,2)
        grid.addWidget(userName, 1,0,1,1)
        grid.addWidget(self.name, 1, 1,1,2)
        grid.addWidget(password1, 2,0,1,1)
        grid.addWidget(self.password, 2, 1,1,2)

        # Labels
        server = QtGui.QLabel("Remote")
        local= QtGui.QLabel("Local")
        grid.addWidget(server, 3, 2,1,1)
        grid.addWidget(local, 3, 7,1,1)

        # Buttons
        grid.addWidget(download, 3, 4,1,1)
        grid.addWidget(upload, 3, 9,1,1)
        grid.addWidget(makeDirectory, 3, 0,1,1)
        grid.addWidget(connectToServer, 2,3,1,1)
        grid.addWidget(disconnectFromServer, 2,4,1,1)
        grid.addWidget(delete, 3,6,1,1)

        # Create file system for server
        self.view = QtGui.QTreeView()
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view.clicked.connect(self.traverseTreeServer)
        self.model = QtGui.QStandardItemModel()
        self.view.setModel(self.model)
        self.view.setUniformRowHeights(True)

        # Stop the filesystem from being editable
        self.view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.view.setHeaderHidden(True)
        self.view.setAlternatingRowColors(True)

        # Add file system to grid
        grid.addWidget(self.view, 4, 0,10,5)

        # Create file system for local
        self.view2 = QtGui.QTreeView()
        self.view2.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view2.clicked.connect(self.traverseTreeClient)
        self.model2 = QtGui.QStandardItemModel()
        self.view2.setModel(self.model2)
        self.view2.setUniformRowHeights(True)

        # Stop the tree from being editable
        self.view2.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.view2.setHeaderHidden(True)
        self.view2.setAlternatingRowColors(True)

        # Add file system to grid
        grid.addWidget(self.view2, 4, 5,10,5)

        # Add textbox to log responses
        self.logOutput = QtGui.QTextEdit()
        self.logOutput.setReadOnly(True)
        self.logOutput.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        grid.addWidget(self.logOutput, 0,7,3,3)
        response= QtGui.QLabel("Server Response")
        grid.addWidget(response, 0,6,1,1)

        # Create widgets in QMainWindow
        widget = QtGui.QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        # Set Window Properties 
        self.setGeometry(500, 500, 1000, 500)
        self.setWindowTitle('FTP Client')
        self.show()

    # Connects the client to the server and calls the functions
    # to populate the filesystems
    def connect_to_server(self):
        self.s = socket.socket()
        ip = self.ipAddress.text()
        port = int( self.port.text() )
        self.username = self.name.text()
        self.password2 = self.password.text()

        self.s.connect((ip, port))
        self.recieve()

        self.action('USER '+ self.username)
        self.action('PASS '+ self.password2)

        # self.action('USER '+'group2')
        # self.action('PASS '+'ei9keNge')
        self.pathServer = self.getPWDServer()
        self.updateTreeClient()
        self.updateTreeServer()

    # Disconnects the client from the server
    def disconnect_from_server(self):
        self.ipAddress.clear()
        self.port.clear()
        self.name.clear()
        self.password.clear()

        self.model.removeRow(0)
        self.model2.removeRow(0)
        self.action('QUIT')
        self.s.close()

    # Requests the server's current working directory and formats it
    def getPWDServer(self):
        mes = ('PWD')
        self.send(mes)
        directory = self.s.recv(1024)
        directory = directory.decode()
        returnCode = directory.split('i')
        returnCode = returnCode[0].split(' ')
        returnCode = returnCode[0]

        if returnCode == '257':
            directory = directory.split('"')
            directory = directory[1]
            print('"'+directory+'"')
        else:
            print('"'+directory+'"')

        return directory

    # Receives and decodes any required messages from th server
    def recieve(self):
        rec = self.s.recv(1024)
        message = rec.decode()
        self.printToLog(message)
        return (rec)

    # Prints the reply messages from the server onto the GUI
    def printToLog(self,message):
        self.logOutput.moveCursor(QtGui.QTextCursor.End)
        self.logOutput.insertPlainText(message)
        self.sb = self.logOutput.verticalScrollBar()
        self.sb.setValue(self.sb.maximum()) 

    # Sends a message using the send() function and calls the receive() 
    # function to receive the reply
    def action(self,mes=''):
	    self.send(mes)
	    return self.recieve()

    # Send a message to the server
    def send(self,mes=''):
	    self.s.send(bytes(mes + ("\r\n"), "UTF-8"))  

    # Informs the server that passive mode should be used
    # Extracts the IP address and port from the server reply 
    def pasv(self):
        while True:
            vali = ''
            mes = ('PASV')
            mes = self.action(mes)
            mes = mes.decode()
            nmsg = mes.split('(')
            nmsg = nmsg[-1].split(')')
            p = nmsg[0].split(',')
            newip = '.'.join(p[:4])
            newport = int(p[4])*256 + int(p[5])
            return (newip,newport)
            break

    # Function to return the current path of the local machine
    def local_dir(self,path=''):
        for (dirpath, dirnames, filenames) in walk(path):
            path = dirpath
            break   
        return path

    # Function to return the directories and files contained
    # within the current path
    def browse_local(self,path=''):
        for (dirpath, dirnames, filenames) in walk(path):
            break
        return (dirnames, filenames)

    def findExtension(self, filename):
        listOfAscii = ['as','asm','asp','atom','atomcat','c','cc',
        'cfm','cgi','conf','cpp','css','csv','def','dhtml','dic','dtd','ecma',
        'es6','es7','f','f77','f90','for','h','hh','hpp','htm','html','java',
        'jhtml','js','js','json','list','log','m','md','mm','opml','p','pas',
        'php','phtml','pl','rb','rss','rt','rtf','rtx','ruby','s','sgm','sgml',
        'sh','shtml','sql','swift','text','tsv','txt','vbs','vcf','vcs','webapp',
        'wri','xht','xhtml','xml','xsl','xsl','xslt','xspf']
        filetype, encoding = mimetypes.guess_type(filename)
        for i in listOfAscii:
            if i in filetype:
                return 'TYPE A'
        return 'TYPE I'

    def defineDownloadType(self):
        print ("Filepathserver: ")
        print(self.filePathServer)
        mes= self.findExtension(self.fileNameServer)
        reply= self.send(mes)
        while True:
            vali = self.recieve()
            vali = vali.decode()
            vali = vali.split("'")
            vali = vali[0].split(' ')
            vali = vali[0]
            
            if vali == '226':
                mes = ('ABOR')
                self.action(mes)
                self.recieve()
                break
            else:
                break

        self.recievefile(self.fileNameServer)

    def defineFileType(self):
        self.filePath ="/" + self.filePath
        file = magic.Magic(mime=True)
        if (file.from_file(self.filePath)=='text/plain'):
            mes = ('TYPE A')
            self.send(mes)
        else:
            mes = ('TYPE I')
            self.send(mes)

        while True:
            vali = self.recieve()
            vali = vali.decode()
            vali = vali.split("'")
            vali = vali[0].split(' ')
            vali = vali[0]
            
            if vali == '226':
                mes = ('ABOR')
                self.action(mes)
                self.recieve()
                break
            else:
                break

        self.action(mes)
        self.sendfile()

    def sendfile(self):
        newip, newport = self.pasv()
        p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p.connect((newip, newport))
        self.send('STOR ' + self.fileName)
        f = open(self.filePath, 'rb')
        size = os.stat(self.filePath)[6]
        opened = True
        pos = 0
        buff = binary_buffer
        packs = size/binary_buffer
        timeb = 100/packs
        i=0

        while opened:
            i=i+timeb

            if i>100:
                i=100

            time.sleep(.05)
            sys.stdout.write("\r%d%%" %i)
            sys.stdout.flush()
            f.seek(pos)
            pos += buff

            if pos >= size:
                piece = f.read(-1)
                opened = False
            else:
                piece = f.read(buff) 
            p.send(piece)
                
            f.seek(pos)

        f.close()
        self.recieve() 

    def recievefile(self,file=''):
        newip, newport = self.pasv()
        p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p.connect((newip, newport))
        self.action('RETR '+file)
        filePath = "/" + self.filePath
        if not os.path.isdir(filePath):
            index=filePath.rfind('/')
            filePath=filePath[:index]
        filePath = filePath + '/'
        fileName = filePath + file
        newfile = open(fileName, 'wb')
        msg=''
        aux=':)'

        while aux != b'':
            time.sleep(.05)
            sys.stdout.write("\r" "wait")
            sys.stdout.flush()
            aux = p.recv(binary_buffer)
            newfile.write(aux)
        newfile.close()
        test= self.recieve()

    def listar(self, pathText):
        mes = ('TYPE A')
        self.action(mes)
        newip, newport = self.pasv()
        p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p.connect((newip, newport))
        mes = ('LIST')
        self.action(mes)
        directory = []

        content =''
        while True:
            data = p.recv(1024)
            data = data.decode()
            if not data:
                break
            content = content + data

        directory = content.split('\r\n')
        directory = directory[:-1]
        folders = []
        files = []

        for item in directory:
            if item[0] == 'd':
                folders.append(item)
            else:
                files.append(item)

        for index, folder in enumerate(folders):
            contents = folder.split(':')
            folder = contents[1]
            folder = folder[3:]
            folders[index] = folder

        for index, file in enumerate(files):
            contents = file.split(':')
            file = contents[1]
            file = file[3:]
            files[index] = file

        print (folders)
        print(files)
        mes = ('ABOR')
        p.send(bytes(mes + ("\r\n"), "UTF-8"))
        self.recieve()
        p.close()
        return (folders,files)

# Open modal for the user to insert file name of file to be created
    def mkdir(self):      
        text, ok = QtGui.QInputDialog.getText(self, 'Create Directory', 
        'Enter the directory name:')
        
        if ok:
            self.newDir=(str(text))
            self.makeNewDirectory()  

# Create a new directory on the server
    def makeNewDirectory(self):
        filePath = self.getPWDServer()
        print("path in makeDirectory: ")
        print (filePath)

        reply = self.action('CWD '+ filePath)
        time.sleep(.05)
        while b'226' in reply:
            reply=self.recieve()

        if b'250' in reply: # directory
            filePath = filePath + '/' + self.newDir

        elif b'550' in reply: # file
            index=filePath.rfind('/')
            filePath=filePath[:index]
            filePath = filePath + '/' + self.newDir

        print("path in makeDirectory 2: ")
        print (filePath)
        self.action('MKD '+filePath)

    def delete(self, answer):
        print("im here")
        if answer.text()== 'OK':
            # filePath = self.getPWDServer()

            # if self.pathServer[0]=='/' and self.pathServer[1]=='/':
            #     self.pathServer=self.pathServer[1:]
            
            reply = self.action('CWD '+ self.pathServer)
            time.sleep(.05)
            while b'226' in reply:
                reply=self.recieve()

            if b'250' in reply: # directory
                mes= "RMD "
                reply=self.action(mes + self.pathServer)

            elif b'550' in reply: # file
                mes= "DELE "
                reply=self.action(mes + self.pathServer)

    # Open modal for the user to insert file name of file to be created
    def deleteDir(self):      
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Are you sure you wish to delete " + self.pathServer + '?')
        msg.setWindowTitle("Confirm delete")
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msg.buttonClicked.connect(self.delete) 
        retval = msg.exec_()

    def getTreePath(self, index):
        path = []
        while index.isValid():
            indexItem = self.model2.index(index.row(), 0, index.parent())
            name = self.model2.itemFromIndex(indexItem).text()
            path.append(name)
            index = index.parent()
        return '/'.join(reversed(path))

    def traverseTreeClient(self,index):
        self.path = self.getTreePath(index)
        self.path = "/" + self.path
        if os.path.isdir(self.path):
            self.updateTreeClient()
            indexItem = self.model2.index(index.row(), 0, index.parent())
            self.fileName = self.model2.itemFromIndex(indexItem).text()
            self.filePath = self.getTreePath(index)
            self.model2.removeRow(0)
        else:
            indexItem = self.model2.index(index.row(), 0, index.parent())
            self.fileName = self.model2.itemFromIndex(indexItem).text()
            self.filePath = self.getTreePath(index)

    def updateTreeClient(self):
        ####### Get directory structure #######
        pathText = self.local_dir(self.path)

        if pathText[0]=="/":
            pathText = pathText[1:]

        newPath = pathText.split('/')

        counter = 0
        child=[]

        for i in newPath:
            child.append(QtGui.QStandardItem(i)) # item 0 is the parent
            child[counter].setIcon(self.dir_all)
            if counter != 0:
                child[counter-1].appendRow([child[counter]])
            counter = counter + 1

        folders, files = self.browse_local(self.path)
        counter2 = 0
        ##### Add folders to tree #####
        for i in folders:
            child.append(QtGui.QStandardItem(i))
            child[counter+counter2].setIcon(self.dir_all)
            child[counter - 1].appendRow([child[counter+counter2]])
            counter2 = counter2 + 1

        counter3 = 0
        ##### Add files to tree #####
        for i in files:
            child.append(QtGui.QStandardItem(i))
            child[counter+counter2+counter3].setIcon(self.file_all)
            child[counter - 1].appendRow([child[counter+counter2+counter3]])
            counter3 = counter3 + 1

        ##### Last step: Add the tree to the model ######
        self.model2.appendRow(child[0])
        self.view2.expandAll()

    def getTreePathServer(self, index):
        path = []
        while index.isValid():
            indexItem = self.model.index(index.row(), 0, index.parent())
            name = self.model.itemFromIndex(indexItem).text()
            path.append(name)
            index = index.parent()
        return '/'.join(reversed(path))

    def traverseTreeServer(self,index):
        self.pathServer = self.getTreePathServer(index)
        print("Path in traverse server ")
        print(self.pathServer)
        if self.pathServer[0]=='/' and self.pathServer[1]=='/':
            self.pathServer=self.pathServer[1:]

        reply = self.action('CWD '+ self.pathServer)
        time.sleep(.05)
        while b'226' in reply:
            reply=self.recieve()

        if b'250' in reply:
            self.updateTreeServer()
            indexItem = self.model.index(index.row(), 0, index.parent())
            self.fileNameServer = self.model.itemFromIndex(indexItem).text()
            self.filePathServer = self.getTreePathServer(index)
            self.model.removeRow(0)
        elif b'550' in reply:
            indexItem = self.model.index(index.row(), 0, index.parent())
            self.fileNameServer = self.model.itemFromIndex(indexItem).text()
            self.filePathServer = self.getTreePathServer(index)

    def updateTreeServer(self):
        # Get current path of server
        pathText = self.getPWDServer()

        print("Path in update " + pathText)

        if pathText[0]=="/" and len(pathText)==1:
            newPath = pathText

        elif pathText[0]=="/":
            newPath = pathText.split('/')
            print(newPath)
            newPath= [x.strip() for x in newPath if x.strip()]
            newPath.insert(0, '/')

        counter = 0
        child=[]
        for i in newPath:
            child.append(QtGui.QStandardItem(i)) # item 0 is the parent
            child[counter].setIcon(self.dir_all)
            if counter != 0:
                child[counter-1].appendRow([child[counter]])
            counter = counter + 1

        folders,files= self.listar(newPath)
        counter2 = 0
        ##### Add folders to tree #####
        for i in folders:
            child.append(QtGui.QStandardItem(i))
            child[counter+counter2].setIcon(self.dir_all)
            child[counter - 1].appendRow([child[counter+counter2]])
            counter2 = counter2 + 1

        counter3 = 0
        ##### Add files to tree #####
        for i in files:
            child.append(QtGui.QStandardItem(i))
            child[counter+counter2+counter3].setIcon(self.file_all)
            child[counter - 1].appendRow([child[counter+counter2+counter3]])
            counter3 = counter3 + 1

        ##### Last step: Add the tree to the model ######
        self.model.appendRow(child[0])
        self.view.expandAll()
            
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
