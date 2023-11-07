import socket
host = 'localhost'
port = 12345
message = "aaaaaaaaaaaaaa"
client_socket = socket.socket()
client_socket.connect((host, port))
client_socket.send(message.encode())
reply =client_socket.recv(1024).decode()
client_socket.close()