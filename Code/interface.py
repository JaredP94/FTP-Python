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
# from client import recieve, action
 
class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):      

        ############# Create grid ####################

        backButtonServer = QtGui.QPushButton("Back")
        download = QtGui.QPushButton("Download")
        upload = QtGui.QPushButton("Upload")
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
        model = QtGui.QFileSystemModel()
        model.setRootPath(QDir.homePath())
        view = QtGui.QTreeView()
        view.setModel(model)

        # model = QtGui.QFileSystemModel()
        # model.setRootPath(QDir.currentPath())
        # view = QtGui.QTreeView()
        # view.setModel(model)
        # view.setRootIndex(model.index(QDir.currentPath()))

        ##### Add file system to grid #####
        grid.addWidget(view, 6, 0,5,5)

        ##### View Tree File System #####
        model2 = QtGui.QFileSystemModel()
        model2.setRootPath(QDir.homePath())
        view2 = QtGui.QTreeView()
        view2.setModel(model2)

        ##### Add file system to grid #####
        grid.addWidget(view2, 6, 6,5,5)

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
        port=int(self.port.text())
        username=self.name.text()
        password=self.password.text()

        self.s.connect((ip, port))
        self.s.recv(1024)

        self.action('USER '+'my_name_is_jeff')
        self.action('PASS '+'strongpassword')

    def disconnect_from_server(self):
        self.ipAddress.clear()
        self.port.clear()
        self.name.clear()
        self.password.clear()
        self.s.close()

    def recieve(self):
	    rec = self.s.recv(1024)
	    return (rec)
	    
    def action(self,mes=''):
	    self.send(mes)
	    return self.recieve()

    def send(self,mes=''):
	    self.s.send(bytes(mes + ("\r\n"), "UTF-8"))       

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()