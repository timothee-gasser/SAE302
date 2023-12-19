import socket
import threading
import mysql.connector
from connect import connection
from administration import kill

server_running = True
client_sockets = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Fonction pour établir la connexion à la base de données
def connect_to_database():
    try:
        db_connection = mysql.connector.connect(
            host="192.168.0.6",
            user="toto",
            password="toto",
            database="SAE302"
        )
        return db_connection
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données : {err}")
        return None

def insert_message_into_db(emetteur, message):
    try:
        db_connection = connect_to_database()
        if db_connection:
            cursor = db_connection.cursor()

            insert_query = "INSERT INTO Histo_msg (h_d_msg, emetteur, msg) VALUES (NOW(), %s, %s)"
            data = (emetteur, message)
            cursor.execute(insert_query, data)
            db_connection.commit()
            cursor.close()
            db_connection.close()
    except mysql.connector.Error as err:
        print(f"Erreur lors de l'insertion du message : {err}")



def handle_client(conn, address):
    global server_running
    authenticated = False
    user_login = None

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
                conn.close()
                break

            elif not authenticated:
                if data.startswith('/connect'):
                    credentials = data.split()[1:]
                    if len(credentials) == 2:
                        login, password = credentials
                        ip = address[0]

                        is_authenticated = connection(f"/connect {login} {password}", ip)
                        if is_authenticated:
                            conn.send("Successfully connected!".encode())
                            print(f"Utilisateur {login} connecté depuis {ip}")
                            authenticated = True
                            user_login = login
                        else:
                            conn.send("Authentication failed. Closing connection.".encode())
                            remove_client(conn)
                            break
                else:
                    conn.send("Please authenticate using /connect <login> <password>".encode())
                    remove_client(conn)
                    break
            elif authenticated:
                if data.startswith('/admin kill'):
                    command_parts = data.split()
                    if len(command_parts) == 3:
                        _, _, username_to_kill = command_parts
                        admin_action(conn, user_login, username_to_kill)

            else:
                print(f"Message du client {address}: {data}")
                insert_message_into_db(user_login, data)
                send_to_other_clients(f"{user_login}: {data}", conn)

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            remove_client(conn)
            break

def admin_action(conn, admin_user, target_user):
    try:
        from administration import kill
        result = kill(admin_user, target_user)
        if result:
            conn.send(f"Admin action performed successfully for '{target_user}'.".encode())
        else:
            conn.send(f"Unable to perform admin action for '{target_user}'.".encode())
    except Exception as e:
        conn.send(f"Error performing admin action: {e}".encode())
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
