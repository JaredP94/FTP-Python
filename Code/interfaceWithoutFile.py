import sys
from PyQt4 import QtGui
from PyQt4.QtGui import (QApplication, QColumnView, QFileSystemModel,
                         QSplitter, QTreeView)
from PyQt4.QtCore import QDir, Qt
import socket
import sys
import os
import time
from time import sleep
from os import walk
 

class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):      

        self.path = os.getcwd()
        ############# Create grid ####################

        backButtonServer = QtGui.QPushButton("Back")
        download = QtGui.QPushButton("Download")
        upload = QtGui.QPushButton("Upload")
        upload.clicked.connect(self.sendfile)
        backButtonClient = QtGui.QPushButton("Back")
        connectToServer = QtGui.QPushButton("Connect")
        connectToServer.clicked.connect(self.connect_to_server)
        disconnectFromServer = QtGui.QPushButton("Disconnect")
        disconnectFromServer.clicked.connect(self.disconnect_from_server)
        grid = QtGui.QGridLayout()
        grid.setSpacing(12) 

        ################ Add widgets to grid ########################
        
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
        grid.addWidget(ip, 0,0)
        grid.addWidget(self.ipAddress, 0,1,1,2)
        grid.addWidget(portLabel, 0,3)
        grid.addWidget(self.port,0,4,1,2)
        grid.addWidget(userName, 1,0,)
        grid.addWidget(self.name, 1, 1,1,2)
        grid.addWidget(password1, 2,0)
        grid.addWidget(self.password, 2, 1,1,2)
        grid.addWidget(connectToServer, 2,3)
        grid.addWidget(disconnectFromServer, 2,4)

        ######## Labels #########
        server = QtGui.QLabel("Remote")
        local= QtGui.QLabel("Local")
        grid.addWidget(server, 4, 2,1,1)
        grid.addWidget(local, 4, 8,1,1)

        ##### Buttons #####
        grid.addWidget(backButtonServer, 4, 0,1,1)
        grid.addWidget(download, 4, 4,1,1)
        grid.addWidget(upload, 4, 10,1,1)
        grid.addWidget(backButtonClient,4, 6,1,1)

        ##### View Tree File System #####
        self.model = QtGui.QFileSystemModel()
        # self.model.setRootPath(QDir.homePath())
        self.view = QtGui.QTreeView()
        self.view.setModel(self.model)

        ##### Add file system to grid #####
        grid.addWidget(self.view, 6, 0,5,5)

        ####### Create manual file system ########
        self.view2 = QtGui.QTreeView()
        self.view2.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view2.clicked.connect(self.pickUploadFile)
        self.model2 = QtGui.QStandardItemModel()
        self.view2.setModel(self.model2)
        self.view2.setUniformRowHeights(True)

        ###### Stop the tree from being editable #######
        self.view2.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        grid.addWidget(self.view2, 6, 6,5,5)
        ####### Create widgets in QMainWindow #######
        widget = QtGui.QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        ####### Window Properties #######
        self.setGeometry(500, 500, 1000, 500)
        self.setWindowTitle('FTP Client')
        self.show()

    def connect_to_server(self):
        self.s = socket.socket()
        ip = self.ipAddress.text()
        port = int( self.port.text() )
        username = self.name.text()
        password = self.password.text()

        self.s.connect((ip, port))
        self.s.recv(1024)

        self.action('USER '+'my_name_is_jeff')
        self.action('PASS '+'strongpassword')
        self.path = self.local_dir()
        self.model.setRootPath(QDir.homePath())

        self.updateTree()

    def disconnect_from_server(self):
        self.ipAddress.clear()
        self.port.clear()
        self.name.clear()
        self.password.clear()
        # self.model.setRootPath(" ")
        self.s.close()

    def pickUploadFile(self,index): ## broken
        indexItem = self.model2.index(index.row(), 0, index.parent())
        self.fileName = self.model2.fileName(indexItem)
        self.filePath = self.getTreePath(index)

    def recieve(self):
	    rec = self.s.recv(1024)
	    return (rec)
	    
    def action(self,mes=''):
	    self.send(mes)
	    return self.recieve()

    def send(self,mes=''):
	    self.s.send(bytes(mes + ("\r\n"), "UTF-8"))  

    def pasv(self):
	    while True:
		    vali = ''
		    mes = ('PASV')
		    self.send(mes)
		    mes = (self.s.recv(1024))
		    mes = mes.decode()
		    nmsg = mes.split('(')
		    nmsg = nmsg[-1].split(')')
		    p = nmsg[0].split(',')
		    newip = '.'.join(p[:4])
		    newport = int(p[4])*256 + int(p[5])
		    return (newip,newport)
		    break

    def local_dir(self,path=''):
        for (dirpath, dirnames, filenames) in walk(path):
            print ('"'+dirpath+'"')
            path = dirpath
            break   
        return path

    def browse_local(self,path=''):
        for (dirpath, dirnames, filenames) in walk(path):
            print (dirnames)
            print (filenames)
            print ('\n')
            break
        return (dirnames, filenames)
		
    def sendfile(self):
        newip, newport = self.pasv()
        p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p.connect((newip, newport))
        self.send('STOR '+self.fileName)
        f = open(self.filePath, 'rb')
        size = os.stat(self.filePath)[6]
        opened = True
        pos = 0
        buff = 1048576
        packs = size/1048576
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

    def updateTree(self):
        self.path = os.getcwd()
        ####### Get directory structure #######
        pathText = self.local_dir(self.path)
        if pathText[0]=="/":
            pathText = pathText[1:]

        newPath = pathText.split('/')
        print(newPath)
        counter = 0
        child=[]
        for i in newPath:
            child.append(QtGui.QStandardItem(i)) # item 0 is the parent
            if counter != 0:
                child[counter-1].appendRow([child[counter]])
            counter = counter + 1

        folders, files = self.browse_local(self.path)
        counter2 = 0
        ##### Add folders to tree #####
        for i in folders:
            child.append(QtGui.QStandardItem(i))
            child[counter - 1].appendRow([child[counter+counter2]])
            counter2 = counter2 + 1

        counter3 = 0
        ##### Add files to tree #####
        for i in files:
            child.append(QtGui.QStandardItem(i))
            child[counter - 1].appendRow([child[counter+counter2+counter3]])
            counter3 = counter3 + 1

        ##### Last step: Add the tree to the model ######
        self.model2.appendRow(child[0])

    def getTreePath(self, index):
    path = []
    while item.isValid():
        indexItem = self.model2.index(index.row(), 0, index.parent())
        self.fileName = self.model2.fileName(indexItem)
        path.append(indexItem)
        index = index.parent()
    return '/'.join(reversed(path))

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()