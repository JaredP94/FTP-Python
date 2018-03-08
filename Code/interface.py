import sys
from PyQt4 import QtGui
from PyQt4.QtGui import (QApplication, QColumnView, QFileSystemModel,
                         QSplitter, QTreeView)
from PyQt4.QtCore import QDir, Qt


class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        ########## Create status bar ###########
        self.statusBar()

        openFile = QtGui.QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        connect = QtGui.QAction('Connect',self)
        connect.setStatusTip("Connect to FTP server")
        connect.triggered.connect(self.openConnectWindow)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu = menubar.addMenu('&Connect')  
        fileMenu.addAction(connect)     

        ########## End create status bar ###########


        ############# Create grid ####################

        backButtonServer = QtGui.QPushButton("Back")
        download = QtGui.QPushButton("Download")
        upload = QtGui.QPushButton("Upload")
        backButtonClient = QtGui.QPushButton("Back")
        connectToServer = QtGui.QPushButton("Connect")
        grid = QtGui.QGridLayout()
        grid.setSpacing(12) 

        ################ Add widgets to grid ########################
        
        ip=QtGui.QLabel("IP Address")
        ipAddress = QtGui.QLineEdit()
        ipAddress.setFixedWidth(150)

        userName=QtGui.QLabel("Username")
        name = QtGui.QLineEdit()
        name.setFixedWidth(150)
	
        password1=QtGui.QLabel("Password")
        password = QtGui.QLineEdit()
        password.setFixedWidth(150)
        password.setEchoMode(QtGui.QLineEdit.Password)
        grid.addWidget(ip, 0,0)
        grid.addWidget(ipAddress, 0,1,1,2)
        grid.addWidget(userName, 1,0,)
        grid.addWidget(name, 1, 1,1,2)
        grid.addWidget(password1, 2,0)
        grid.addWidget(password, 2, 1,1,2)
        grid.addWidget(connectToServer, 2,3)

        # spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        # grid.addItem(spacerItem, 3, 0, 1, 8)

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
        
    def showDialog(self):

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                '/home')
        
        f = open(fname, 'r')
        
        with f:        
            data = f.read()
            self.textEdit.setText(data) 

    def textchanged(self):
        print "contents of text box: "+self.text

    def openConnectWindow(self): 
        text, ok = QtGui.QInputDialog.getText(self, 'Connect to server', 
        'Enter the IP address to connect to:')
        
        if ok and text:
            self.le.setText(str(text))
            self.username   

    def username(self):      
        text2, ok = QtGui.QInputDialog.getText(self, 'Log in', 
        'Enter your username:')
        
        if ok:
            self.le.setText(str(text2))                         

    def password(self):      
        text, ok = QtGui.QInputDialog.getText(self, 'Log in', 
        'Enter your password:')
        
        if ok:
            self.le.setText(str(text))  

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()