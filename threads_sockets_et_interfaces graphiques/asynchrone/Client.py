import socket
import threading

def receive_messages(sock):
    while True:
        try:
            reply = sock.recv(1024).decode()
            if not reply:
                print("Le serveur s'est déconnecté")
                break
            print("Serveur :", reply)

        except Exception as e:
            print(f"Une erreur s'est produite lors de la réception des messages : {e}")
            break

host = '127.0.0.1'
port = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((host, port))
    print(f"Connecté au serveur sur {host}:{port}")

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    client_en_marche = True

    while client_en_marche:
        try:
            message = input("Ton message ('bye' pour quitter ou 'arret' pour arrêter le serveur) : ")
            client_socket.send(message.encode())

            if message.lower() == 'bye':
                print("Le serveur s'est déconnecté")
                client_socket.close()
                break

            if message.lower() == 'arret':
                print("Arrêt du serveur demandé")
                client_socket.close()
                client_en_marche = False
                break

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            break

except Exception as e:
    print(f"Erreur lors de la connexion au serveur : {e}")

finally:
    client_socket.close()
