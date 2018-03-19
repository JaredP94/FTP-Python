import socket
import sys
import os
import time
from time import sleep
from os import walk

s = socket.socket()

binary_buffer = 4194304

def send(mes=''):
	s.send(bytes(mes + ("\r\n"), "UTF-8"))

def recieve():
	rec = s.recv(1024)
	return (rec)
	    
def action(mes=''):
	send(mes)
	return recieve()

def local_dir(path=''):
	for (dirpath, dirnames, filenames) in walk(path):
		print ('"'+dirpath+'"')
		break

def browse_local(path=''):
	for (dirpath, dirnames, filenames) in walk(path):
		print (dirnames)
		print (filenames)
		print ('\n')
		break

def pasv():
	while True:
		vali = ''
		mes = ('PASV')
		send(mes)
		mes = (s.recv(1024))
		mes = mes.decode()
		nmsg = mes.split('(')
		nmsg = nmsg[-1].split(')')
		p = nmsg[0].split(',')
		newip = '.'.join(p[:4])
		newport = int(p[4])*256 + int(p[5])
		return (newip,newport)
		break
		
def sendfile(file=''):
	newip, newport = pasv()
	p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	p.connect((newip, newport))
	send('STOR '+file)
	filepath = path + '/' + file
	f = open(filepath, 'rb')
	size = os.stat(filepath)[6]
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
	recieve()

def recievefile(file=''):
	newip, newport = pasv()
	p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	p.connect((newip, newport))
	action('RETR '+file)
	newfile = open(file, 'wb')
	msg=''
	aux=':)'

	while aux != b'':
		time.sleep(.05)
		sys.stdout.write("\r" "wait")
		sys.stdout.flush()
		aux = p.recv(binary_buffer)
		newfile.write(aux)
	newfile.close()

def listar():
	newip, newport = pasv()
	p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	p.connect((newip, newport))
	mes = ('LIST')
	action (mes)
	directory = []

	time.sleep(.05)
	content = p.recv(1024)
	content = content.decode()
	print(content)
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

	print(folders)
	print(files)

	mes = ('ABOR')
	p.send(bytes(mes + ("\r\n"), "UTF-8"))
	recieve()

address = input("Enter FTP Address: ")
port = int(input("Enter FTP Port: "))
s.connect((address, port))
s.recv(1024)		
		
action('USER '+'group2')
action('PASS '+'ei9keNge')

path = os.getcwd()
buff=1024

while True:
	os.system('cls' if os.name == 'nt' else 'clear')
	print ('1 - Print Local and Remote Directory')
	print ('2 - Change Directory')
	print ('3 - Send Files')
	print ('4 - Recieve Files')
	print ('5 - Change Permissions')
	print ('6 - Exit')
	selection = input('Select an option: ')

	if selection == '1':
		while True:
			directory = ''
			os.system('cls' if os.name == 'nt' else 'clear')
			print('Remote Directory')
			mes = ('PWD')
			send(mes)
			directory = s.recv(1024)
			directory = directory.decode()
			vali = directory.split('i')
			vali = vali[0].split(' ')
			vali = vali[0]

			if vali == '257':
				directory = directory.split('"')
				directory = directory[1]
				print('"'+directory+'"')
			else:
				print('"'+directory+'"')

			listar()
			print('\nLocal Directory')
			local_dir(path)
			browse_local(path)
			print(input('\nHit Return'))
			break

	if selection == '2':
		while True:
			os.system('cls' if os.name == 'nt' else 'clear')
			print ('1 - Change Local Directory')
			print ('2 - Change Remote Directory')
			print ('3 - Return to Previous Menu')
			selection2 = input('Select an option: ')

			if selection2 == '1':
				path2 = input('Change local directory (write home to return to home directory): ')

				if path2 == 'home':
					path = '/home/'
				else: 
					path = (path+path2+'/')

				browse_local(path)
				print(input('\nHit Return'))

			if selection2 == '2':
				print('Change remote directory (write up to go one directory up)')
				rd = input("Specify directory: ")

				if rd == 'up':
					action('CDUP')
				else:
					action('CWD '+rd)

				listar()
				print(input('\nHit Return'))

			if selection2 == '3':
				break

	if selection == '3':
		while True:
			os.system('cls' if os.name == 'nt' else 'clear')
			print ('File type')
			print ('1 - ASCII')
			print ('2 - Image')
			print ('3 - Return to Previous Menu')
			selection2 = input('Select an option: ')

			if selection2 == '1':
				os.path = path
				file = input('File Name: ')
				mes = ('TYPE A')
				send(mes)

				while True:
					vali = recieve()
					vali = vali.decode()
					vali = vali.split("'")
					vali = vali[0].split(' ')
					vali = vali[0]

					if vali == '226':
						mes = ('ABOR')
						action(mes)
						recieve()
						break
					else:
						break

				action(mes)
				sendfile(file)
				print(input('\nHit Return'))

			if selection2 == '2':
				os.path = path
				file = input('File Name: ')
				mes = ('TYPE I')
				send(mes)
				
				while True:
					vali = recieve()
					vali = vali.decode()
					vali = vali.split("'")
					vali = vali[0].split(' ')
					vali = vali[0]

					if vali == '226':
						mes = ('ABOR')
						action(mes)
						recieve()
						break
					else:
						break

				sendfile(file)
				print(input('\nHit Return'))

			if selection2 == '3':
				break

	if selection == '4':
		while True:
			os.system('cls' if os.name == 'nt' else 'clear')
			print ('File type')
			print ('1 - ASCII')
			print ('2 - Image')
			print ('3 - Return')
			selection2 = input('Select an option: ')

			if selection2 == '1':
				os.path = path
				file = input('File Name: ')
				mes = ('TYPE A')
				send(mes)

				while True:
					vali = recieve()
					vali = vali.decode()
					vali = vali.split("'")
					vali = vali[0].split(' ')
					vali = vali[0]

					if vali == '226':
						mes = ('ABOR')
						action(mes)
						recieve()
						break
					else:
						break

				recievefile(file)
				print(input('\nHit Return'))
				
			if selection2 == '2':
				os.path = path
				file = input('File Name: ')
				mes = ('TYPE I')
				send(mes)

				while True:
					vali = recieve()
					vali = vali.decode()
					vali = vali.split("'")
					vali = vali[0].split(' ')
					vali = vali[0]

					if vali == '226':
						mes = ('ABOR')
						action(mes)
						recieve()
						break
					else:
						break

				recievefile(file)
				print(input('\nHit Return'))
				
			if selection2 == '3':
				break
				
	if selection == '5':
		os.system('cls' if os.name == 'nt' else 'clear')
		file=input('File name: ')
		perm=input('Write permissions in hexadecimal, Example (742) :')
		action('SITE CHMOD '+ perm + ' ' + file)
		print('the permissions of '+ file +' has been updated to ' + perm)
		print(input('\nHit Return'))

	if selection == '6':
		os.system('cls' if os.name == 'nt' else 'clear')
		print('FTP client now exiting')
		print(input('\nHit return to exit'))
		send('QUIT')
		break

s.close()                  