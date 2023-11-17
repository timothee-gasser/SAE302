import socket
import threading

server_running = True  # Variable de contrôle du serveur

def reception(conn, address):
    global server_running  # Référence à la variable globale
    while server_running:
        try:
            data = conn.recv(1024).decode()

            if not data:
                print(f"Le client {address} s'est déconnecté")
                break

            if data.lower() == 'bye':
                bye = "ok bye"
                conn.send(bye.encode())
                print(f"Le client {address} s'est déconnecté")
                break

            elif data.lower() == 'arret':
                arret = "ok arret"
                conn.send(arret.encode())
                print(f"Arrêt du serveur demandé par le client {address}")
                server_running = False  # Modifier la variable pour arrêter le serveur
                break

            else:
                response = "bien recu"
                conn.send(response.encode())
                print(f"Message du client : {data}")

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            break

def send_message(conn):
    while True:
        message_to_send = input("Entrez le message à envoyer au client ('exit' pour quitter) : ")
        if message_to_send.lower() == 'exit':
            break

        try:
            conn.send(message_to_send.encode())
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'envoi du message : {e}")
            break

host = '0.0.0.0'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Le serveur écoute sur {host}:{port}")

    while True:
        conn, address = server_socket.accept()
        print(f"Connexion entrante de {address}")

        reception_thread = threading.Thread(target=reception, args=(conn, address))
        reception_thread.start()

        send_thread = threading.Thread(target=send_message, args=(conn,))
        send_thread.start()



except Exception as e:
    print(f"Erreur lors de la création du serveur : {e}")

finally:
    server_socket.close()
