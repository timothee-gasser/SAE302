import socket
import threading
from connect import connection

server_running = True
client_sockets = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def handle_client(conn, address):
    global server_running
    authenticated = False  # Variable pour suivre l'état d'authentification du client
    user_login = None  # Pour stocker le login de l'utilisateur authentifié

    while server_running:
        try:
            data = conn.recv(1024).decode()

            if not data:
                print(f"Le client {address} s'est déconnecté")
                remove_client(conn)
                break

            if data.lower() == 'bye':
                bye = "ok bye"
                conn.send(bye.encode())
                print(f"Le client {address} s'est déconnecté")
                remove_client(conn)
                break

            elif data.lower() == 'arret':
                arret = "ok arret"
                conn.send(arret.encode())
                print(f"Arrêt du serveur demandé par le client {address}")
                server_running = False
                remove_client(conn)
                break

            elif not authenticated:  # Si l'utilisateur n'est pas encore authentifié
                if data.startswith('/connect'):
                    credentials = data.split()[1:]  # Extraction des identifiants
                    if len(credentials) == 2:
                        login, password = credentials
                        ip = address[0]  # Récupération de l'adresse IP du client

                        # Vérification de l'authentification
                        is_authenticated = connection(f"/connect {login} {password}", ip)
                        if is_authenticated:
                            conn.send("Successfully connected!".encode())
                            print(f"Utilisateur {login} connecté depuis {ip}")
                            authenticated = True  # Authentification réussie
                            user_login = login  # Enregistrement du login de l'utilisateur
                        else:
                            conn.send("Authentication failed. Closing connection.".encode())
                            remove_client(conn)
                            break
                else:
                    conn.send("Please authenticate using /connect <login> <password>".encode())
                    remove_client(conn)
                    break

            else:  # Une fois authentifié, l'utilisateur peut envoyer des messages normalement
                print(f"Message du client {address}: {data}")
                send_to_other_clients(f"{user_login}: {data}", conn)

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            remove_client(conn)
            break

def send_to_other_clients(message, sender_conn):
    for client_conn, address in client_sockets.items():
        if client_conn != sender_conn:
            try:
                client_conn.send(message.encode())
            except Exception as e:
                print(f"Erreur lors de l'envoi du message aux clients : {e}")
                remove_client(client_conn)



def remove_client(client_conn):
    if client_conn in client_sockets:
        del client_sockets[client_conn]
        client_conn.close()

def start_server():
    host = '0.0.0.0'
    port = 12345

    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Le serveur écoute sur {host}:{port}")

        while server_running:
            conn, address = server_socket.accept()
            print(f"Connexion entrante de {address}")

            client_sockets[conn] = address

            client_thread = threading.Thread(target=handle_client, args=(conn, address))
            client_thread.start()

        server_socket.close()

    except Exception as e:
        print(f"Erreur lors de la création du serveur : {e}")

    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
