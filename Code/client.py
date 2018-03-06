#!/usr/bin/python           				# This is client.py file
				
import socket               				# Import socket module
	
### TCP SOCKET ### 	
s = socket.socket()         				# Create a socket object
host = socket.gethostname() 				# Get local machine name
port = 8000               				# Reserve a port for your service.

s.connect((host, port))
print(s.recv(1024).decode("utf-8"))
while True:
	message = input('Enter a message: ')                # Obtain message to send
	s.send(bytes(message, 'UTF-8'))
	print(s.recv(1024).decode("utf-8"))
	if message == 'exit':			       # Close connection is exit command sent
		print('ending session')
		break
s.close()						   # Close the socket when done