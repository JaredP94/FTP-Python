import os,socket,threading,time
#import traceback

allow_delete = True
local_ip = socket.gethostbyname(socket.gethostname())
local_port = 8000
currdir=os.path.abspath('.')

class FTPserverThread(threading.Thread):
    def __init__(self,conn,addr):
        self.conn = conn
        self.addr = addr
        self.basewd = currdir
        self.cwd = self.basewd
        self.rest = False
        self.pasv_mode = False
        self.mode = None
        self.dataAddr = None
        self.dataPort = None
        threading.Thread.__init__(self)

    def run(self): #works
        self.conn.send(bytes('220 Welcome!\r\n', 'UTF-8'))
        while True:
            cmd=self.conn.recv(256).decode("utf-8")
            if not cmd: break
            else:
                print ('Recieved:',cmd)
                try:
                    func=getattr(self,cmd[:4].strip().upper())
                    func(cmd)
                except Exception as e:
                    print ('ERROR:',e)
                    #traceback.print_exc()
                    self.conn.send(bytes('500 Sorry.\r\n', 'UTF-8'))

    def SYST(self,cmd): #works
        self.conn.send(bytes('215 UNIX Type: L8\r\n', 'UTF-8'))

    def OPTS(self,cmd): #works
        if cmd[5:].upper()=='UTF8 ON':
            self.conn.send(bytes('200 OK.\r\n', 'UTF-8'))
        else:
            self.conn.send(bytes('451 Sorry.\r\n', 'UTF-8'))

    def USER(self,cmd): #works
        self.conn.send(bytes('331 OK.\r\n', 'UTF-8'))

    def PASS(self,cmd): #works
        self.conn.send(bytes('230 OK.\r\n', 'UTF-8'))
        #self.conn.send('530 Incorrect.\r\n')

    def QUIT(self,cmd): #works
        self.conn.send(bytes('221 Goodbye.\r\n','UTF-8'))

    def NOOP(self,cmd): #works
        self.conn.send(bytes('200 OK.\r\n','UTF-8'))

    def TYPE(self,cmd): #works
        self.mode=cmd[5]
        self.conn.send(bytes('200 Binary mode.\r\n', 'UTF-8'))

    def CDUP(self,cmd): #works
        if not os.path.samefile(self.cwd,self.basewd):
            #learn from stackoverflow
            self.cwd=os.path.abspath(os.path.join(self.cwd,'..'))
        self.conn.send(bytes('200 OK.\r\n','UTF-8'))

    def PWD(self,cmd): #works
        cwd=os.path.relpath(self.cwd,self.basewd)
        if cwd=='.':
            cwd='/'
        else:
            cwd='/'+cwd
        self.conn.send(bytes('257 \"%s\"\r\n' % cwd, 'UTF-8'))

    def CWD(self,cmd): #works
        chwd=cmd[4:]
        if chwd=='/':
            self.cwd=self.basewd
        elif chwd[0]=='/':
            self.cwd=os.path.join(self.basewd,chwd[1:])
        else:
            self.cwd=os.path.join(self.cwd,chwd)
        self.conn.send(bytes('250 OK.\r\n', 'UTF-8'))

    def PORT(self,cmd):
        if self.pasv_mode:
            self.servsock.close()
            self.pasv_mode = False
        l=cmd[5:].split(',')
        self.dataAddr='.'.join(l[:4])
        self.dataPort=(int(l[4])<<8)+int(l[5])
        self.conn.send(bytes('200 Get port.\r\n', 'UTF-8'))

    def PASV(self,cmd): # from http://goo.gl/3if2U
        self.pasv_mode = True
        self.servsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.servsock.bind((local_ip,0))
        self.servsock.listen(1)
        ip, port = self.servsock.getsockname()
        print ('open', ip, port)
        self.conn.send(bytes('227 Entering Passive Mode (%s,%u,%u).\r\n' %
                (','.join(ip.split('.')), port>>8&0xFF, port&0xFF), 'UTF-8'))

    def start_datasock(self):
        if self.pasv_mode:
            self.datasock, addr = self.servsock.accept()
            print ('connect:', addr)
        else:
            self.datasock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.datasock.connect((self.dataAddr,self.dataPort))

    def stop_datasock(self):
        self.datasock.close()
        if self.pasv_mode:
            self.servsock.close()


    def LIST(self,cmd):
        self.conn.send(bytes('150 Here comes the directory listing.\r\n', 'UTF-8'))
        print ('list:', self.cwd)
        self.start_datasock()
        for t in os.listdir(self.cwd):
            k=self.toListItem(os.path.join(self.cwd,t))
            self.datasock.send(k+'\r\n')
        self.stop_datasock()
        self.conn.send(bytes('226 Directory send OK.\r\n', 'UTF-8'))

    def toListItem(self,fn):
        st=os.stat(fn)
        fullmode='rwxrwxrwx'
        mode=''
        for i in range(9):
            mode+=((st.st_mode>>(8-i))&1) and fullmode[i] or '-'
        d=(os.path.isdir(fn)) and 'd' or '-'
        ftime=time.strftime(' %b %d %H:%M ', time.gmtime(st.st_mtime))
        return d+mode+' 1 user group '+str(st.st_size)+ftime+os.path.basename(fn)

    def MKD(self,cmd): #works
        dn=os.path.join(self.cwd,cmd[4:])
        os.mkdir(dn)
        self.conn.send(bytes('257 Directory created.\r\n', 'UTF-8'))

    def RMD(self,cmd): #works
        dn=os.path.join(self.cwd,cmd[4:])
        if allow_delete:
            os.rmdir(dn)
            self.conn.send(bytes('250 Directory deleted.\r\n', 'UTF-8'))
        else:
            self.conn.send(bytes('450 Not allowed.\r\n', 'UTF-8'))

    def DELE(self,cmd): #works
        fn=os.path.join(self.cwd,cmd[5:])
        if allow_delete:
            os.remove(fn)
            self.conn.send(bytes('250 File deleted.\r\n', 'UTF-8'))
        else:
            self.conn.send(bytes('450 Not allowed.\r\n', 'UTF-8'))

    def RNFR(self,cmd): #works
        self.rnfn=os.path.join(self.cwd,cmd[5:])
        self.conn.send(bytes('350 Ready.\r\n', 'UTF-8'))

    def RNTO(self,cmd): #works
        fn=os.path.join(self.cwd,cmd[5:])
        os.rename(self.rnfn,fn)
        self.conn.send(bytes('250 File renamed.\r\n', 'UTF-8'))

    def REST(self,cmd):
        self.pos=int(cmd[5:])
        self.rest=True
        self.conn.send(bytes('250 File position reseted.\r\n', 'UTF-8'))

    def RETR(self,cmd):
        fn=os.path.join(self.cwd,cmd[5:])
        #fn=os.path.join(self.cwd,cmd[5:-2]).lstrip('/')
        print ('Downlowding:',fn)
        if self.mode=='I':
            fi=open(fn,'rb')
        else:
            fi=open(fn,'r')
        self.conn.send(bytes('150 Opening data connection.\r\n', 'UTF-8'))
        if self.rest:
            fi.seek(self.pos)
            self.rest=False
        data= fi.read(1024)
        self.start_datasock()
        while data:
            self.datasock.send(data)
            data=fi.read(1024)
        fi.close()
        self.stop_datasock()
        self.conn.send(bytes('226 Transfer complete.\r\n', 'UTF-8'))

    def STOR(self,cmd):
        fn=os.path.join(self.cwd,cmd[5:])
        print ('Uploading:',fn)
        if self.mode=='I':
            fo=open(fn,'wb')
        else:
            fo=open(fn,'w')
        self.conn.send(bytes('150 Opening data connection.\r\n', 'UTF-8'))
        self.start_datasock()
        while True:
            data=self.datasock.recv(1024)
            if not data: break
            fo.write(data)
        fo.close()
        self.stop_datasock()
        self.conn.send(bytes('226 Transfer complete.\r\n', 'UTF-8'))

class FTPserver(threading.Thread):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((local_ip,local_port))
        threading.Thread.__init__(self)

    def run(self):
        self.sock.listen(5)
        while True:
            th=FTPserverThread(*self.sock.accept())
            th.daemon=True
            th.start()

    def stop(self):
        self.sock.close()

if __name__=='__main__':
    ftp=FTPserver()
    ftp.daemon=True
    ftp.start()
    print ('On', local_ip, ':', local_port)
    input('Enter to end...\n')
    ftp.stop()