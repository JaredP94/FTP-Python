import os
import socket
import stat
import sys
import threading
import time
import magic
from pathlib import Path
from utils import fileProperty

try:
    host = socket.gethostbyname(socket.gethostname())
except socket.gaierror:
    host = socket.gethostname()

port = 8000
working_directory  = os.getcwd()
allow_delete = False
ascii_buffer = 1024
binary_buffer = 4194304

class FTPServerProtocol(threading.Thread):
    def __init__(self, command_socket, address):
        threading.Thread.__init__(self)
        self.authenticated      = False
        self.pasv_mode          = False
        self.rest               = False
        self.working_directory  = working_directory
        self.command_socket     = command_socket
        self.address            = address
        self.type               = 'A'
        self.mode               = 'S'

    def run(self):
        # Handles and executes received user commands
        self.connectionSuccess()
        while True:
            try:
                data = self.command_socket.recv(ascii_buffer).rstrip()
                try:
                    client_command = data.decode('utf-8')
                except AttributeError:
                    client_command = data
                log('Received data', client_command)
                if not client_command:
                    break
            except socket.error as error:
                log('Receive', error)

            try:
                client_command, param = client_command[:4].strip().upper(), client_command[4:].strip() or None
                func = getattr(self, client_command)
                func(param)
            except AttributeError as error:
                self.sendResponse('500 Syntax error, command unrecognized.\r\n')
                log('Receive', error)

    def connectionSuccess(self):
        # Provide greeting for accepted user connection
        self.sendResponse('220 Welcome.\r\n')

    #=======================================#
    ## FTP transmission control procedures ##
    #=======================================#
    def createDataSocket(self):
        # Open socket with client for data transmission
        log('createDataSocket', 'Opening a data channel')
        try:
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.pasv_mode:
                self.data_socket, self.address = self.server_socket.accept()

            else:
                self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_socket.connect((self.data_socket_address, self.data_socket_port))
        except socket.error as error:
            log('createDataSocket', error)

    def terminateDataSocket(self):
        # Close data tranmission socket with client
        log('terminateDataSocket', 'Closing a data channel')
        try:
            self.data_socket.close()
            if self.pasv_mode:
                self.server_socket.close()
        except socket.error as error:
            log('terminateDataSocket', error)

    def sendResponse(self, client_command):
        # Transmit request codes and relevant message to client
        self.command_socket.send(client_command.encode('utf-8'))

    def sendData(self, data):
        # Transmit file data to client
        if self.type == 'I':
            self.data_socket.send(data)
        else:
            self.data_socket.send(data.encode('utf-8'))

    #===============================================#
    ## FTP commands and additional functionalities ##
    #===============================================#
    def USER(self, username):
        # Lets user to set their username
        log("USER", username)
        if not username:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')
        else:
            self.sendResponse('331 User name okay, need password.\r\n')
            self.username = username

    def PASS(self, password):
        # Lets user to set their password
        log("PASS", password)
        if not password:
            self.sendResponse('501 Syntax error in parameters or arguments.\r\n')

        elif not self.username:
            self.sendResponse('503 Bad sequence of commands.\r\n')

        else:
            self.sendResponse('230 User logged in, proceed.\r\n')
            self.password = password
            self.authenticated = True

    def TYPE(self, type):
        # Specify file mode to be handled
        log('TYPE', type)
        self.type = type

        if self.type == 'I':
            self.sendResponse('200 Binary file mode.\r\n')
        elif self.type == 'A':
            self.sendResponse('200 Ascii file mode.\r\n')

    def PASV(self, client_command):
        # Makes server-DTP "listen" on a non-default data port to wait for a connection rather than initiate one upon receipt of a transfer command
        log("PASV", client_command)
        self.pasv_mode  = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, 0))
        self.server_socket.listen(5)
        address, port = self.server_socket.getsockname()
        self.sendResponse('227 Entering Passive Mode (%s,%u,%u).\r\n' %
                (','.join(address.split('.')), port>>8&0xFF, port&0xFF))

    def MODE(self, mode):
        # Specifies data transfer mode for server
        log('MODE', mode)
        self.mode = mode

        if self.type == 'S':
            self.sendResponse('200 Stream transfer mode.\r\n')
        elif self.type == 'B':
            self.sendResponse('200 Block transfer mode.\r\n')
        elif self.type == 'C':
            self.sendResponse('200 Compressed transfer mode.\r\n')


    def PORT(self,client_command):
        # Specify the port to be used for data transmission
        log("PORT: ", client_command)
        if self.pasv_mode:
            self.server_socket.close()
            self.pasv_mode = False

        connection_info = client_command[5:].split(',')
        self.data_socket_address = '.'.join(connection_info[:4])
        self.data_socket_address = (int(connection_info[4])<<8) + int(connection_info[5])
        self.sendResponse('200 Get port.\r\n')

    def LIST(self, directory_path):
        # Sends list of content in specified server path
        if not self.authenticated:
            self.sendResponse('530 User not logged in.\r\n')
            return

        if not directory_path:
            server_path = os.path.abspath(os.path.join(self.working_directory, '.'))
        elif directory_path.startswith(os.path.sep):
            server_path = os.path.abspath(directory_path)
        else:
            server_path = os.path.abspath(os.path.join(self.working_directory, directory_path))

        log('LIST', server_path)

        if not self.authenticated:
            self.sendResponse('530 User not logged in.\r\n')
        elif not os.path.exists(server_path):
            self.sendResponse('550 LIST failed Path name not exists.\r\n')
        else:
            self.sendResponse('150 Here is listing.\r\n')
            self.createDataSocket()

            if not os.path.isdir(server_path):
                fileMessage = fileProperty(server_path)
                self.data_socket.sock(fileMessage+'\r\n')
            else:
                for file in os.listdir(server_path):
                    fileMessage = fileProperty(os.path.join(server_path, file))
                    self.sendData(fileMessage+'\r\n')

            self.terminateDataSocket()
            self.sendResponse('226 List done.\r\n')

    def NLST(self, directory_path):
        # Sends a directory listing from server to user site
        self.LIST(directory_path)

    def CWD(self, directory_path):
        # Allows user to change current directory to a new directory on the server
        server_path = directory_path.endswith(os.path.sep) and directory_path or os.path.join(self.working_directory, directory_path)
        log('CWD', server_path)

        if not os.path.exists(server_path) or not os.path.isdir(server_path):
            self.sendResponse('550 CWD failed Directory not exists.\r\n')
            return

        self.working_directory = server_path
        self.sendResponse('250 CWD Command successful.\r\n')

    def PWD(self, client_command):
        # Returns the current server directory path
        log('PWD', client_command)
        self.sendResponse('257 "%s".\r\n' % self.working_directory)

    def CDUP(self, client_command):
        # Changes current working directory to parent directory
        self.working_directory = os.path.abspath(os.path.join(self.working_directory, '..'))
        log('CDUP', self.working_directory)
        self.sendResponse('200 OK.\r\n')

    def DELE(self, filename):
        # Deletes file specified in the pathname to be deleted at the server site
        server_path = filename.endswith(os.path.sep) and filename or os.path.join(self.working_directory, filename)
        log('DELE', server_path)

        if not self.authenticated:
            self.sendResponse('530 User not logged in.\r\n')
        elif not os.path.exists(server_path):
            self.send('550 DELE failed File %s not exists.\r\n' % server_path)
        elif not allow_delete:
            self.send('450 DELE failed delete not allow.\r\n')
        else:
            os.remove(server_path)
            self.sendResponse('250 File deleted.\r\n')

    def MKD(self, dirname):
        # Creates specified directory at current path directory
        server_path = dirname.endswith(os.path.sep) and dirname or os.path.join(self.working_directory, dirname)
        log('MKD', server_path)

        if not self.authenticated:
            self.sendResponse('530 User not logged in.\r\n')
        else:
            try:
                os.mkdir(server_path)
                self.sendResponse('257 Directory created.\r\n')
            except OSError:
                self.sendResponse('550 MKD failed Directory "%s" already exists.\r\n' % server_path)

    def RMD(self, dirname):
        # Removes specified directory at current path directory
        import shutil
        server_path = dirname.endswith(os.path.sep) and dirname or os.path.join(self.working_directory, dirname)
        log('RMD', server_path)

        if not self.authenticated:
            self.sendResponse('530 User not logged in.\r\n')
        elif not allow_delete:
            self.sendResponse('450 Directory deleted.\r\n')
        elif not os.path.exists(server_path):
            self.sendResponse('550 RMDIR failed Directory "%s" not exists.\r\n' % server_path)
        else:
            shutil.rmtree(server_path)
            self.sendResponse('250 Directory deleted.\r\n')

    def RNFR(self, filename):
        # Specifies the old pathname of the file which is to be renamed
        server_path = filename.endswith(os.path.sep) and filename or os.path.join(self.working_directory, filename)
        log('RNFR', server_path)

        if not os.path.exists(server_path):
            self.sendResponse('550 RNFR failed File or Directory %s not exists.\r\n' % server_path)
        else:
            self.rnfr = server_path

    def RNTO(self, filename):
        # Specifies the new pathname of the file specified in the immediately preceding "rename from" command
        server_path = filename.endswith(os.path.sep) and filename or os.path.join(self.working_directory, filename)
        log('RNTO', server_path)

        if not os.path.exists(os.path.sep):
            self.sendResponse('550 RNTO failed File or Direcotry  %s not exists.\r\n' % server_path)
        else:
            try:
                os.rename(self.rnfr, server_path)
            except OSError as error:
                log('RNTO', error)

    def REST(self, pos):
        # Represents the server marker at which file transfer is to be restarted
        self.pos  = int(pos)
        log('REST', self.pos)
        self.rest = True
        self.sendResponse('250 File position reseted.\r\n')

    def RETR(self, filename):
        # Causes server-DTP to transfer a copy of the file, specified in the pathname, to the server- or user-DTP at the other end of the data connection
        server_path = os.path.join(self.working_directory, filename)
        log('RETR', server_path)

        if not os.path.exists(server_path):
            return
        try:
            if self.type=='I':
                file = open(server_path, 'rb')
            else:
                file = open(server_path, 'r')
        except OSError as error:
            log('RETR', error)

        self.sendResponse('150 Opening data connection.\r\n')

        if self.rest:
            file.seek(self.pos)
            self.rest = False

        self.createDataSocket()

        while True:
            data = file.read(binary_buffer)
            if not data: break
            if self.mode == 'S':
                self.sendData(data)

        file.close()
        self.terminateDataSocket()
        self.sendResponse('226 Transfer complete.\r\n')

    def STOR(self, filename):
        # Causes the server-DTP to accept the data transferred via the data connection and to store the data as a file at the server site
        if not self.authenticated:
            self.sendResponse('530 STOR failed User not logged in.\r\n')
            return

        server_path = os.path.join(self.working_directory, filename)
        log('STOR', server_path)

        try:
            if self.type == 'I':
                file = open(server_path, 'wb')
            else:
                file = open(server_path, 'w')
        except OSError as error:
            log('STOR', error)

        self.sendResponse('150 Opening data connection.\r\n' )
        self.createDataSocket()

        while True:
            if self.type == 'I':
                data = self.data_socket.recv(binary_buffer)
            else:
                data = self.data_socket.recv(binary_buffer).decode('utf-8')

            if not data:
                break

            file.write(data)

        file.close()
        self.terminateDataSocket()
        self.sendResponse('226 Transfer completed.\r\n')

    def APPE(self, filename):
        # Causes the server-DTP to accept the data transferred via the data connection and to store the data in a file at the server site
        # If file specified in pathname exists at server site, the data shall be appended to that file; otherwise the file shall be created at the server site.
        if not self.authenticated:
            self.sendResponse('530 APPE failed User not logged in.\r\n')
            return

        server_path = filename.endswith(os.path.sep) and filename or os.path.join(self.working_directory, filename)
        log('APPE', server_path)
        self.sendResponse('150 Opening data connection.\r\n')
        self.createDataSocket()

        if not os.path.exists(server_path):
            if self.type == 'I':
                file = open(server_path, 'wb')
            else:
                file = open(server_path, 'w')
            while True:
                data = self.data_socket.recv(ascii_buffer)
                if not data:
                    break
                file.write(data)

        else:
            n = 1

            while not os.path.exists(server_path):
                filename, extname = os.path.splitext(server_path)
                server_path = filename + '(%s)' %n + extname
                n += 1

            if self.type == 'I':
                file = open(server_path, 'wb')
            else:
                file = open(server_path, 'w')
            while True:
                data = self.data_socket.recv(ascii_buffer)
                if not data:
                    break
                file.write(data)

        file.close()
        self.terminateDataSocket()
        self.sendResponse('226 Transfer completed.\r\n')

    def SYST(self, param):
        # Used to find out the type of operating system at the server
        log('SYS', param)
        self.sendResponse('215 %s type.\r\n' % sys.platform)

    def NOOP(self, client_command):
        # Specifies no action other than that the server send an OK reply
        log('NOOP', client_command)
        self.sendResponse('200 OK.\r\n')

    def HELP(self, param):
        # Provides server command list to client
        log('HELP', param)
        help = """
            214
            USER [name], Its argument is used to specify the user's string. It is used for user authentication.
            PASS [password], Its argument is used to specify the user password string.
            PASV The directive requires server-DTP in a data port.
            PORT [h1, h2, h3, h4, p1, p2] The command parameter is used for the data connection data port
            LIST [directory_path or filename] This command allows the server to send the list to the passive DTP. If
                 the pathname specifies a path or The other set of files, the server sends a list of files in
                 the specified directory. Current information if you specify a file path name, the server will
                 send the file.
            CWD  Type a directory path to change working directory.
            PWD  Get current working directory.
            CDUP Changes the working directory on the remote host to the parent of the current directory.
            DELE Deletes the specified remote file.
            MKD  Creates the directory specified in the RemoteDirectory parameter on the remote host.
            RNFR [old name] This directive specifies the old pathname of the file to be renamed. This command
                 must be followed by a "heavy Named "command to specify the new file pathname.
            RNTO [new name] This directive indicates the above "Rename" command mentioned in the new path name
                 of the file. These two Directive together to complete renaming files.
            REST [position] Marks the beginning (REST) ​​The argument on behalf of the server you want to re-start
                 the file transfer. This command and Do not send files, but skip the file specified data checkpoint.
            RETR This command allows server-FTP send a copy of a file with the specified path name to the data
                 connection The other end.
            STOR This command allows server-DTP to receive data transmitted via a data connection, and data is
                 stored as A file server site.
            APPE This command allows server-DTP to receive data transmitted via a data connection, and data is stored
                 as A file server site.
            SYS  This command is used to find the server's operating system type.
            HELP Displays help information.
            QUIT This command terminates a user, if not being executed file transfer, the server will shut down
                 Control connection\r\n.
            """
        self.sendResponse(help)

    def QUIT(self, param):
        # Connected user logs out and disconnects from server if not transfer in progress
        log('QUIT', param)
        self.sendResponse('221 Goodbye.\r\n')

    def IDIR(self, pathServer):
        # Determines whether path exists on server site
        if os.path.isdir(pathServer):
            self.sendResponse('True')
            log("IDIR", 'True')
        else:
            self.sendResponse('False')
            log("IDIR", 'False')

    def FTYP(self, pathServer): # file type
        file = magic.Magic(mime=True)
        if (file.from_file(pathServer)=='text/plain'):
            self.sendResponse('True')
        else:
            self.sendResponse('False')

def log(func, client_command):
    # Provides logger service for server activity
    log_message = time.strftime("%Y-%m-%d %H-%M-%S [-] " + func)
    print("\033[31m%s\033[0m: \033[32m%s\033[0m" % (log_message, client_command))

def serverListener():
    global listen_socket
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((host, port))
    listen_socket.listen(5)

    log('Server started', 'Listen on: %s, %s' % listen_socket.getsockname())
    while True:
        connection, address = listen_socket.accept()
        ftp_connection_instance = FTPServerProtocol(connection, address)
        ftp_connection_instance.start()
        log('Accept', 'Created a new connection %s, %s' % address)

if __name__ == "__main__":
    log('Start FTP server', 'Enter EXIT to stop FTP server...')
    listener = threading.Thread(target=serverListener)
    listener.start()

    if input().lower() == "exit":
        listen_socket.close()
        log('Server stop', 'Server closed')
        sys.exit()
