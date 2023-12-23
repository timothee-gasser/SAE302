import socket
import threading
import mysql.connector
from connect import connection
from administration import *
import datetime

sign_up_open = False
server_running = True
client_sockets = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pseudo_to_address = {}

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
        logs(f"Erreur de connexion à la base de données : {err}")
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
        logs(f"Erreur lors de l'insertion du message : {err}")



def handle_client(conn, address):
    global server_running
    authenticated = False
    user_login = None

    while server_running:
        try:
            data = conn.recv(1024).decode()

            if not data:
                logs(f"Le client {address} s'est déconnecté")
                remove_client(conn)
                break

            if data.lower() == 'bye':
                bye = "ok bye"
                conn.send(bye.encode())
                logs(f"Le client {address} s'est déconnecté")
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
                            conn.send("Bien jouer t'est co".encode())
                            logs(f"Utilisateur {login} connecté depuis {ip}")
                            authenticated = True
                            user_login = login
                            pseudo_to_address[user_login] = address
                        else:
                            conn.send("Authentication failed. Closing connection.".encode())
                            remove_client(conn)
                            break
                elif data.startswith('/sign-up'):
                    if sign_up_open:
                        command_parts = data.split()
                        if len(command_parts) == 3:
                            ip = address[0]
                            _, username, password = command_parts
                            signup_result = sign_up(username, password)
                            if signup_result:
                                conn.send("Inscription réussie. Nouveau compte créé.".encode())
                                conn.send("Bien jouer t'est co".encode())
                                logs(f"Utilisateur {username} connecté depuis {ip}")
                                authenticated = True
                                user_login = username
                                pseudo_to_address[user_login] = address
                            else:
                                conn.send("Erreur lors de l'inscription. Veuillez réessayer.".encode())
                        else:
                            conn.send("Format incorrect. Utilisation : /sign-up <nom_util> <mdp>".encode())
                    else:
                        conn.send("La création de compte sur ce serveur à était désactiver".encode())

                else:
                    conn.send("Please authenticate using /connect <login> <password>".encode())
                    remove_client(conn)
                    break
            elif authenticated:

                if data.startswith('/admin kill'):
                    command_parts = data.split(maxsplit=3)
                    if len(command_parts) >= 3:
                        _, _, username_to_kill, reason_to_kill = command_parts
                        admin_action(conn, user_login, username_to_kill, reason_to_kill)
                    else:
                        conn.send("Le format n'est pas bon. C'est : /admin kill <nom> <raison>".encode())

                elif data.startswith('/admin ban'):
                    command_parts = data.split(maxsplit=3)
                    if len(command_parts) >= 3:
                        _, _, user_to_ban, reason_to_ban = command_parts
                        admin_ban_action(conn, user_login, user_to_ban, reason_to_ban)
                    else:
                        conn.send("Le format n'est pas bon. C'est : /admin ban <nom ou ip> <raison>".encode())

                elif data.startswith('/admin kick'):
                    command_parts = data.split(maxsplit=4)
                    if len(command_parts) >= 4:
                        _, _, user_to_kick, duree, reason_to_kick = command_parts
                        admin_kick_action(conn, user_login, user_to_kick, duree, reason_to_kick)
                    else:
                        conn.send(
                            "Le format n'est pas bon. C'est : /admin kick <nom_utilisateur> <durée_en_min> <raison>".encode())
                elif data.startswith('/demande'):
                    command_parts = data.split(maxsplit=2)
                    if len(command_parts) >= 3:
                        _, type_demande, demande_text = command_parts
                        demande(user_login, type_demande, demande_text)
                        conn.send("Demande enregistrée avec succès.".encode())
                    else:
                        conn.send("Le format n'est pas bon. C'est : /demande <type_de_demande> <demande>".encode())

                elif data.startswith('/admin demande'):
                    admin_demande(user_login, conn)

                elif data.startswith('/admin ticket'):
                    command_parts = data.split(maxsplit=4)
                    if len(command_parts) >= 4:
                        _, _, id_demande, etat_demande, commentaire = command_parts
                        success = ticket(user_login, id_demande, etat_demande, commentaire)
                        if success:
                            conn.send("Demande mise à jour avec succès.".encode())
                        else:
                            conn.send("Échec de la mise à jour de la demande.".encode())
                    else:
                        conn.send(
                            "Le format n'est pas bon. C'est : /admin ticket <id_demande> <etat_demande> <commentaire>".encode())

                elif data.startswith('/ticket'):
                    user_tickets_info = user_tickets(user_login)
                    conn.send(user_tickets_info.encode())



                else:
                    print(f"Message du client {address}: {data}")
                    insert_message_into_db(user_login, data)
                    send_to_other_clients(f"{user_login}: {data}", conn)

        except Exception as e:
            logs(f"Une erreur s'est produite : {e}")
            remove_client(conn)
            break
def admin_kick_action(conn, admin_user, target_user, duree, reason):
    try:
        result = kick(admin_user, target_user, duree, reason)
        if result:
            conn.send(f"Utilisateur '{target_user}' est kick pendant {duree} minutes.".encode())

            for username, address in pseudo_to_address.items():
                if username == target_user:
                    for client_conn, conn_address in client_sockets.items():
                        if conn_address == address:
                            remove_client(client_conn)
                            conn.send(f"Utilisateur '{target_user}' a été déconnecté.".encode())
                            break
        else:
            conn.send(f"Impossible d'effectuer l'action de kick pour '{target_user}'.".encode())
    except Exception as e:
        conn.send(f"Erreur lors de l'action de kick : {e}".encode())

def admin_ban_action(conn, admin_user, target_user_or_ip, reason):
    global client_sockets, pseudo_to_address
    try:
        result = ban(admin_user, target_user_or_ip, reason, admin_user)
        if result:
            conn.send(f"Utilisateur ou IP '{target_user_or_ip}' est banni.".encode())

            if '@' not in target_user_or_ip:
                for username, address in pseudo_to_address.items():
                    if username == target_user_or_ip:
                        for client_conn, conn_address in client_sockets.items():
                            if conn_address == address:
                                remove_client(client_conn)
                                conn.send(f"Utilisateur '{target_user_or_ip}' a été déconnecté.".encode())
                                break
            else:
                for client_conn, address in client_sockets.items():
                    if client_conn != conn and address[0] == target_user_or_ip:
                        remove_client(client_conn)
                        conn.send(f"Tous les utilisateurs utilisant l'IP '{target_user_or_ip}' ont été déconnectés.".encode())
        else:
            conn.send(f"Impossible d'effectuer l'action de bannissement pour '{target_user_or_ip}'.".encode())
    except Exception as e:
        conn.send(f"Erreur lors de l'action de bannissement : {e}".encode())

def admin_action(conn, admin_user, target_user, reason=None):  # Ajoutez le paramètre reason
    try:
        result = kill(admin_user, target_user, reason)  # Passez la raison à la fonction kill
        if result:
            conn.send(f"Tu à kill '{target_user}'.Il c'est fait déco.".encode())
            for username, addr in pseudo_to_address.items():
                if username == target_user:  # Vérifie si l'utilisateur est connecté
                    for client_conn, client_addr in client_sockets.items():
                        if client_addr == addr:  # Trouve la connexion correspondante
                            remove_client(client_conn)  # Ferme la connexion
                            break
                    break


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
                logs(f"Erreur lors de l'envoi du message aux clients : {e}")
                remove_client(client_conn)


def update_user_status(username, status):
    try:
        db_connection = connect_to_database()
        if db_connection:
            cursor = db_connection.cursor()

            update_query = "UPDATE Utilisateur SET etat_util = %s WHERE login = %s"
            data = (status, username)
            cursor.execute(update_query, data)
            db_connection.commit()
            cursor.close()
            db_connection.close()
    except mysql.connector.Error as err:
        logs(f"Erreur lors de la mise à jour de l'état de l'utilisateur : {err}")


def remove_client(client_conn):
    if client_conn in client_sockets:
        address = client_sockets[client_conn]
        username = [user for user, addr in pseudo_to_address.items() if addr == address]
        if username:
            update_user_status(username[0], "deco")

        del client_sockets[client_conn]
        client_conn.close()


def start_server():
    host = '0.0.0.0'
    port = 12345

    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        logs(f"Le serveur écoute sur {host}:{port}")

        while server_running:
            conn, address = server_socket.accept()
            logs(f"Connexion entrante de {address}")

            client_sockets[conn] = address

            client_thread = threading.Thread(target=handle_client, args=(conn, address))
            client_thread.start()

        server_socket.close()

    except Exception as e:
        logs(f"Erreur lors de la création du serveur : {e}")

    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()