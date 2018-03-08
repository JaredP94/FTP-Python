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
        forwardButtonServer = QtGui.QPushButton("Forward")
        download = QtGui.QPushButton("Download")
        upload = QtGui.QPushButton("Upload")
        backButtonClient = QtGui.QPushButton("Back")
        forwardButtonClient = QtGui.QPushButton("Forward")
        grid = QtGui.QGridLayout()
        grid = QtGui.QGridLayout()
        grid.setSpacing(10) 

        ################ Add widgets to grid ########################

        ##### Buttons #####
        grid.addWidget(backButtonServer, 1, 1, 1, 1)
        grid.addWidget(forwardButtonServer, 1, 2)
        grid.addWidget(download, 1, 3)
        grid.addWidget(upload, 1, 7)
        grid.addWidget(backButtonClient, 1, 8)
        grid.addWidget(forwardButtonClient, 1, 9)

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
        grid.addWidget(view, 2, 0, 5, 5)

        ##### View Tree File System #####
        model2 = QtGui.QFileSystemModel()
        model2.setRootPath(QDir.homePath())
        view2 = QtGui.QTreeView()
        view2.setModel(model2)

        # model = QtGui.QFileSystemModel()
        # model.setRootPath(QDir.currentPath())
        # view = QtGui.QTreeView()
        # view.setModel(model)
        # view.setRootIndex(model.index(QDir.currentPath()))

        ##### Add file system to grid #####
        grid.addWidget(view2, 2, 6, 5, 5)

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

    def openConnectWindow(self):      
        text, ok = QtGui.QInputDialog.getText(self, 'Connect to server', 
        'Enter the IP address to connect to:')
        
        if ok:
            self.le.setText(str(text))                           
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()