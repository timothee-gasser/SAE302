import socket

host = 'localhost'
port = 12345


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print(f"Le serveur écoute sur {host}:{port}")
while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connexion entrante de {client_address}")
    data = client_socket.recv(1024).decode()
    print(f"Message reçu du client : {data}")
    response = "Message reçu avec succès!"
    client_socket.send(response.encode())
    client_socket.close()
