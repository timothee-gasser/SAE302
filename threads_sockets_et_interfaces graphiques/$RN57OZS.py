import socket

host = '0.0.0.0'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print(f"Le serveur écoute sur {host}:{port}")

conn, address = server_socket.accept()
print(f"Connexion entrante de {address}")

while True:
    data = conn.recv(1024).decode()

    if not data:
        print(f"Le client {address} s'est déconnecté")
        break

    if data.lower() == 'bye':
        bye = "ok bye"
        conn.send(bye.encode())
        print(f"Le client {address} s'est déconnecté")
        break

    response = "bien recu"
    conn.send(response.encode())
    print(f"Message du client : {data}")

conn.close()
server_socket.close()
print("Arrêt du serveur")
