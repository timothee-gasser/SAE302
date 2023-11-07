import socket

host = '127.0.0.1'
port = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

while True:
    message = input("Ton message (ou 'bye' pour quitter) : ")
    client_socket.send(message.encode())
    reply = client_socket.recv(1024).decode()
    print("Serveur :", reply)
    if message.lower() == 'bye':
        break
    if message.lower() == 'arret':
        break
client_socket.close()
