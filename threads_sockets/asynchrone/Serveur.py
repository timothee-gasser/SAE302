import socket
import threading

server_running = True
client_sockets = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def handle_client(conn, address):
    global server_running
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

            else:
                print(f"Message du client {address}: {data}")
                send_to_other_clients(data, conn)

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            remove_client(conn)
            break

def send_to_other_clients(message, sender_conn):
    sender_address = client_sockets[sender_conn]
    for client_conn, address in client_sockets.items():
        if client_conn != sender_conn:
            try:
                client_conn.send(f"{sender_address}: {message}".encode())
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
