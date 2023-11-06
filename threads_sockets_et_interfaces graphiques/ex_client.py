import socket


host = 'localhost'
port = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


client_socket.connect((host, port))
message = "bye"
client_socket.send(message.encode())
data = client_socket.recv(1024).decode()
print("Données reçues du serveur :", data)


