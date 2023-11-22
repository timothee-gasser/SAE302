import socket
import threading

def handle_client(conn, address):
    connected = True
    while connected:
        try:
            data = conn.recv(1024).decode()

            if not data:
                print(f"Le client {address} s'est déconnecté")
                connected = False
                break

            if data.lower() == 'bye':
                bye = "ok bye"
                conn.send(bye.encode())
                print(f"Le client {address} s'est déconnecté")
                connected = False
                break

            elif data.lower() == 'arret':
                arret = "ok arret"
                conn.send(arret.encode())
                print(f"Arrêt du serveur demandé par le client {address}")
                connected = False
                break

            else:
                response = "bien recu"
                conn.send(response.encode())
                print(f"Message du client {address}: {data}")

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            break

    conn.close()

def start_server():
    host = '0.0.0.0'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Le serveur écoute sur {host}:{port}")

        while True:
            conn, address = server_socket.accept()
            print(f"Connexion entrante de {address}")

            client_thread = threading.Thread(target=handle_client, args=(conn, address))
            client_thread.start()

    except Exception as e:
        print(f"Erreur lors de la création du serveur : {e}")
    finally:
        server_socket.close()

start_server()
