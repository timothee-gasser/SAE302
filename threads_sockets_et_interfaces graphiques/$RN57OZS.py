import socket

host = '0.0.0.0'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print(f"Le serveur écoute sur {host}:{port}")

conn, address = server_socket.accept()
print(f"Connexion entrante de {address}")

serveur_en_marche = True

while serveur_en_marche:
    data = conn.recv(1024).decode()

    if not data:
        print(f"Le client {address} s'est déconnecté")
        break

    if data.lower() == 'bye':
        bye = "ok bye"
        conn.send(bye.encode())
        print(f"Le client {address} s'est déconnecté")
        serveur_en_marche = True
        conn.close()
        print(f"Le serveur écoute sur {host}:{port}")
        conn, address = server_socket.accept()

    elif data.lower() == 'arret':
        bye = "ok arret"
        conn.send(bye.encode())
        print(f"Arrêt du serveur demandé par le client {address}")
        serveur_en_marche = False
        conn.close()
        print("Arrêt du serveur")
    else:
        response = "bien recu"
        conn.send(response.encode())
        print(f"Message du client : {data}")

server_socket.close()
