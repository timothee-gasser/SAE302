import socket

host = '127.0.0.1'
port = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

client_en_marche = True

while client_en_marche:
    message = input("Ton message ('bye' pour quitter ou 'arret' pour arreter le serveurdfhfg) : ")
    client_socket.send(message.encode())
    reply = client_socket.recv(1024).decode()

    if not reply:
        print("Le serveur s'est déconnecté")
        break

    if message.lower() == 'bye':
        print("Le serveur s'est déconnecté")
        client_socket.close()
        break

    if message.lower() == 'arret':
        print("Arrêt du serveur demandé")
        client_socket.close()
        client_en_marche = False

    print("Serveur :", reply)

client_socket.close()
