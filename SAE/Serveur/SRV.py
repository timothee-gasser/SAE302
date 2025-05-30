import socket
import threading
from connect import connection
from administration import *
"""
Programe principale du serveur.
"""

sign_up_open = False
server_running = True
client_sockets = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pseudo_to_address = {}

def insert_message_into_db(emetteur, message, name_salon=None):
    """
        Insère un message dans la base de données.

        Args:
            emetteur (str): L'émetteur du message.
            message (str): Le contenu du message.
            name_salon (str, optionnel): Le nom du salon. Par défaut, None.
        """
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()
            if name_salon == None:
                insert_query = "INSERT INTO Histo_msg (h_d_msg, emetteur, msg) VALUES (NOW(), %s, %s)"
                data = (emetteur, message)
                cursor.execute(insert_query, data)
                db_connection.commit()
                cursor.close()
                db_connection.close()
            else:
                id_salon = get_salon_id(cursor, name_salon)
                insert_query = "INSERT INTO Histo_msg (h_d_msg, emetteur, msg, id_salon) VALUES (NOW(), %s, %s, %s)"
                data = (emetteur, message,id_salon)
                cursor.execute(insert_query, data)
                db_connection.commit()
                cursor.close()
                db_connection.close()

    except mysql.connector.Error as err:
        logs(f"Erreur lors de l'insertion du message : {err}")
def handle_client(conn, address):
    """
        Gère les actions pour chaque client connecté.C'est Ici que tout les message seront décortiquer.

        Args:
            conn (socket): La connexion du client.
            address (tuple): L'adresse IP et le port du client.
        """
    global server_running
    global sign_up_open

    authenticated = False
    user_login = None

    while server_running:
        try:
            data = conn.recv(1024).decode()
            if not data:
                logs(f"Le client {address} s'est déconnecté")
                remove_client(conn)
                break
            if data.lower() == '/bye':
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
                            if is_authenticated == "admin":
                                conn.send("admin".encode())
                            else:
                                conn.send("co".encode())
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
                                conn.send("co".encode())
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
                        if username_to_kill == "serveur":
                            send_to_clients("Le serveur va s'arrêter. Vous allez être déconnecté.")
                            for client_conn in list(client_sockets.keys()):
                                remove_client(client_conn)
                            server_running = False
                            server_socket.close()
                            break
                        else:
                            
                            admin_kill(conn, user_login, username_to_kill, reason_to_kill)
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
                elif data.startswith('/demande_salon'):
                    insert_message_into_db(user_login, data)
                    command_parts = data.split(maxsplit=2)
                    if len(command_parts) >= 2:
                        _, salon_name, raison = command_parts
                        result = demande_salon(user_login, salon_name, raison)
                        if result == "success":
                            conn.send("Demande de salon enregistrée avec succès.".encode())
                        elif result == "open":
                            conn.send("Vous avez été ajouté au salon.".encode())
                        elif result == "closed":
                            conn.send("Le salon est fermé, demande enregistrée.".encode())
                        else:
                            conn.send("Impossible de traiter la demande de salon.".encode())
                    else:
                        conn.send("Format incorrect. Utilisation : /demande_salon <nom_salon> <raison>".encode())
                elif data.startswith('/admin demande_salon_update'):
                    insert_message_into_db(user_login, data)
                    command_parts = data.split(maxsplit=3)
                    if len(command_parts) >= 3:
                        _, _, id_demande_salon, etat_demande_salon = command_parts
                        success = demande_salon_update(user_login, id_demande_salon, etat_demande_salon)
                        if success:
                            conn.send("Demande de salon mise à jour avec succès.".encode())
                        else:
                            conn.send("Échec de la mise à jour de la demande de salon.".encode())
                    else:
                        conn.send(
                            "Le format n'est pas bon. C'est : /admin demande_salon_update <id_demande_salon> <etat_demande_salon(yes or no)>".encode())
                elif data.startswith('/admin demande_salon'):
                    insert_message_into_db(user_login, data)
                    admin_demande_salon(user_login, conn)
                elif data.startswith('/demande'):
                    command_parts = data.split(maxsplit=2)
                    if len(command_parts) >= 3:
                        _, type_demande, demande_text = command_parts
                        demande(user_login, type_demande, demande_text)
                        conn.send("Demande enregistrée avec succès.".encode())
                    else:
                        conn.send("Le format n'est pas bon. C'est : /demande <type_de_demande> <demande>".encode())
                elif data.lower() == '/liste salon':
                    db_connection = connect_to_db()
                    if db_connection:
                        cursor = db_connection.cursor()
                        user_id = get_user_id(cursor, user_login)
                        if user_id:
                            salon_list = liste_salons(user_id)
                            conn.send(f"{salon_list}".encode())
                            logs(f"Le client {user_login} à récupérer les salon")

                        else:
                            conn.send("ID utilisateur non trouvé.".encode())
                        db_connection.close()
                elif data.lower() == '/liste util':
                    db_connection = connect_to_db()
                    if db_connection:
                        cursor = db_connection.cursor()
                        user_id = get_user_id(cursor, user_login)
                        if user_id:
                            user_list = liste_util(user_login)
                            conn.send(user_list.encode())
                        else:
                            conn.send("ID utilisateur non trouvé.".encode())
                        db_connection.close()
                elif data.startswith('/admin demande'):
                    insert_message_into_db(user_login, data)
                    admin_demande(user_login, conn)
                elif data.startswith('/admin ticket'):
                    insert_message_into_db(user_login, data)
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
                elif data.startswith('/admin sign-up'):
                    insert_message_into_db(user_login, data)
                    command_parts = data.split(maxsplit=2)
                    db_connection = connect_to_db()
                    if db_connection:
                        cursor = db_connection.cursor()
                        if check_admin_privileges(cursor, user_login):
                            if len(command_parts) >= 2:
                                _, _, etat_sign = command_parts
                                if etat_sign == "open":
                                    sign_up_open= True
                                    conn.send("Enregitrement de nouveaux utilisateur ouvert".encode())
                                elif etat_sign == "close":
                                    sign_up_open = False
                                    conn.send("Enregitrement de nouveaux utilisateur fermer".encode())
                                else:
                                    conn.send("Cette comende accept uniquement 'open' et 'close'".encode())
                            else:
                                conn.send(
                                    "Le format n'est pas bon. C'est : /admin sign-up <open-close>".encode())
                        else:
                            conn.send("Vous n'avez pas les autorisations nécessaires pour cette commande.".encode())
                        db_connection.close()
                elif data.lower() == '/help' or data.lower() == '/?':
                    help_text = "Bienvenue sur le serveur de chat. Voici quelques commandes disponibles :\n" \
                                "/help ou /? : Affiche cette aide\n" \
                                "/admin help ou /admin ? : Affiche l'aide pour les admins\n" \
                                "/demande <Type de demande> <Demande>: permet de créer des demande qui seront directement envoyer aux admin. Le type de demande est souvent Ban,Kick,Kill\n" \
                                "/ticket : Permet de voir l'avancer de vos ticket (demande)\n" \
                                "/sign-up <nom> <mot de passe>: Cette commande s'exécute avant la connexion. Elle permet de créer un nouveau compte.\n" \
                                "/liste salon : Cette commande vous permet de lister tous les salon, si il est ouvert(besoin uniquement d'une demande) ou fermer(besoin d'être accepté par les admins), et si vous en fait partie True ou False.\n" \
                                "/liste util: Cette commende vous permet de lister tout les utilisateur et savoir si ils sont connecter ou pas\n" \
                                "/salon <nom_salon> : Vous permet d'envoyer un message dans un salon(cela fonctionne segment si vous êtes autorisé à parler dans ce salon. \n" \
                                "/demande salon <nom_salon> <raison>: Cette commende vous permet de demander à rejoindre un salon. Si c'est un salon ouvert vous serai directement ajouter. Si c'est un salon fermer un administrateur devra vous autorisé"
                    conn.send(help_text.encode())
                elif data.lower() == '/admin help' or data.lower() == '/admin ?':
                    db_connection = connect_to_db()
                    if db_connection:
                        cursor = db_connection.cursor()
                        if check_admin_privileges(cursor, user_login):
                            admin_help_text = "Bienvenue, je voit que tu est un admin, tu peux donc utiliser les commande suivante :\n" \
                                                "/admin kill <username-serveur> <raison> : Pour tuer un utilisateur ou etaindre le serveur\n" \
                                                "/admin ban <username ou IP> <raison> : Pour bannir un utilisateur ou une IP\n" \
                                                "/admin kick <username> <durée_en_min> <raison> : Pour expulser un utilisateur\n" \
                                                "/admin demande : Pour voir les demandes\n" \
                                                "/admin ticket <id_demande> <etat_demande> <commentaire> : Pour gérer les tickets\n"\
                                                "/admin demande_salon: Cette commende vous permet de lister toutes les demande pour rejoindre les salon\n" \
                                                "/admin demande_salon_update <id_demande_salon> <etat_demande_salon(yes ou no)> : En utilisant cette commende vous pouvez accepter ou refuser une demande d'un utilisateur pour rejoindre un salon\n" \
                                                "/admin sign-up <open/close>: Cette commende permet à de nouveau utilisateur ou pas de rejoindre le serveur"
                            conn.send(admin_help_text.encode())
                        else:
                            conn.send("Vous n'avez pas les autorisations nécessaires pour cette commande.".encode())
                        db_connection.close()
                elif data.startswith('/ticket'):
                    insert_message_into_db(user_login, data)
                    user_tickets_info = user_tickets(user_login)
                    conn.send(user_tickets_info.encode())
                elif data.startswith('/salon'):
                    command_parts = data.split(maxsplit=2)
                    if len(command_parts) >= 3:
                        _, salon_name, salon_message = command_parts
                        tagged_message = salon(user_login, salon_name, salon_message)
                        if tagged_message.startswith(":"):
                            insert_message_into_db(user_login,salon_message, salon_name)
                            send_to_salon_members(tagged_message, salon_name)
                        else:
                            conn.send(tagged_message.encode())
                    else:
                        conn.send("Le format n'est pas correct. Utilisation : /salon <nom_salon> <message>".encode())
                else:
                    insert_message_into_db(user_login, data)
                    print(f"Message du client {address}: {data}")
                    send_to_clients(f":general {user_login}: {data}")
        except Exception as e:
            logs(f"Une erreur s'est produite : {e}")
            remove_client(conn)
            break
def admin_kick_action(conn, admin_user, target_user, duree, raison):
    """
        Exécute l'action de kick (deconection du client pendant un sertain temps).

        Args:
            conn (socket): La connexion du client administrateur.
            admin_user (str): Le nom de l'administrateur exécutant l'action.
            target_user (str): Le nom de l'utilisateur à kick.
            duree (int): La durée du kick en minutes.
            raison (str): La raison du kick.

        Notes:
            Tout les kick sont documenter dans la BDD.
        """
    try:
        result = kick(admin_user, target_user, duree, raison)
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
def admin_ban_action(conn, admin_user, target_user_or_ip, raison):
    """
        Exécute une action de bannissement sur un utilisateur ou une adresse IP.

        Args:
            conn (socket): La connexion du client administrateur.
            admin_user (str): Le nom de l'administrateur exécutant l'action.
            target_user_or_ip (str): Le nom de l'utilisateur ou l'adresse IP à bannir.
            raison (str): La raison du bannissement.

        Notes:
            Tout les banissement sont documenter dans la BDD.
        """
    global client_sockets, pseudo_to_address
    try:
        result = ban(admin_user, target_user_or_ip, raison)
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
def admin_kill(conn, admin_user, target_user, raison=None):
    """
        Exécute l'action kill qui permet de deconecter un clien .

        Args:
            conn (socket): La connexion du client administrateur.
            admin_user (str): Le nom de l'administrateur exécutant l'action.
            target_user (str): Le nom de l'utilisateur à kill.
            raison (str, optionnel): La raison du kill. Par défaut, None.

        Notes:
            Tout les kill sont documenter dans la BDD.
    """
    try:
        result = kill(admin_user, target_user, raison)
        if result:
            conn.send(f"Tu à kill '{target_user}'.Il c'est fait déco.".encode())
            for username, addr in pseudo_to_address.items():
                if username == target_user:
                    for client_conn, client_addr in client_sockets.items():
                        if client_addr == addr:
                            remove_client(client_conn)
                            break
                    break


        else:
            conn.send(f"Unable to perform admin action for '{target_user}'.".encode())
    except Exception as e:
        conn.send(f"Error performing admin action: {e}".encode())
def send_to_clients(message):
    """
        Envoie un message à tous les autres clients connectés.

        Args:
            message (str): Le message à envoyer.

        Notes:
            Cette fonction envoie le message spécifié à tous les clients connectés.
            En cas d'erreur lors de l'envoi du message à un client spécifique, ce client
            est retiré de la liste des clients connectés.Cela evite certaines erreurs.
        """
    for client_conn, address in client_sockets.items():
        try:
            client_conn.send(message.encode())
        except Exception as e:
            logs(f"Erreur lors de l'envoi du message aux clients : {e}")
            remove_client(client_conn)
def send_to_salon_members(message, salon_name):
    """
        Envoie un message à tous les membres d'un salon spécifique.

        Args:
            message (str): Le message à envoyer.
            salon_name (str): Le nom du salon auquel le message doit être envoyé.

        Notes:
            Elle récupère d'abord les membres du salon depuis la base de données et envoie ensuite le message
            à chaque membre connecté du salon.

    """
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()
            salon_members = get_salon_members(cursor, salon_name)
            for username, address in pseudo_to_address.items():
                member_id = get_user_id(cursor, username)
                if member_id in salon_members:
                    try:
                        matching_conns = [conn for conn, addr in client_sockets.items() if addr == address]
                        if matching_conns:
                            client_conn = matching_conns[0]
                            client_conn.send(message.encode())

                    except Exception as e:
                        logs(f"Erreur lors de l'envoi du message aux clients : {e}")
                        remove_client(client_conn)

            db_connection.close()

    except mysql.connector.Error as error:
        logs(f"Error: {error}")
        return "Une erreur s'est produite lors de l'envoi du message dans le salon."
def update_user_status(username, status):
    """
        Met à jour le statut d'un utilisateur dans la base de données.

        Args:
            username (str): Le nom d'utilisateur à mettre à jour.
            status (str): Le nouveau statut de l'utilisateur (connect ou deco).

        Notes:
            Cette fonction met à jour l'état (ou statut) d'un utilisateur dans la base de données.
            Elle exécute directement une requête SQL pour modifier l'état de l'utilisateur spécifié.

    """
    try:
        db_connection = connect_to_db()
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
    """
        Supprime un client de la liste des clients connectés et met à jour son statut.

        Args:
            client_conn (socket): La connexion du client à supprimer.

        Notes:
            Cette fonction retire un client spécifique de la liste des clients connectés. Elle identifie l'utilisateur
            associé à la connexion du client à l'aide des informations stockées dans les dictionnaires `client_sockets`
            et `pseudo_to_address`. Ensuite, elle met à jour le statut de déconnexion de l'utilisateur, s'il est connecté,
            en appelant la fonction `update_user_status`. Enfin, elle ferme la connexion du client.

        """
    if client_conn in client_sockets:
        address = client_sockets[client_conn]
        username = [user for user, addr in pseudo_to_address.items() if addr == address]
        if username:
            update_user_status(username[0], "deco")

        del client_sockets[client_conn]
        client_conn.close()
def start_server():
    """
        Lance le serveur.

        Notes:
            Cette fonction initialise et lance le serveur sur l'addresse 0.0.0.0 et un port donner par l'utilisateur. Elle écoute
            les connexions entrantes et crée des threads pour gérer les clients connectés en appelant la fonction
            'handle_client'.
    """
    host = '0.0.0.0'
    port = int(input("Port d'écoute du serveur: "))

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