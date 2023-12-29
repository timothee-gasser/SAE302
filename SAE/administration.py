import mysql.connector
from datetime import datetime, timedelta
def connect_to_db():
    try:
        db_connection = mysql.connector.connect(
            host="185.39.142.44",
            port="3333",
            user='toto',
            password='toto',
            database='SAE302'
        )
        return db_connection
    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return None
def check_admin_privileges(cursor, admin_user):
    admin_query = "SELECT type_util FROM Utilisateur WHERE login = %s"
    cursor.execute(admin_query, (admin_user,))
    admin_result = cursor.fetchone()
    if admin_result and admin_result[0] == 'admin':
        return True
    return False
def check_user_in_salon(cursor, user_id, salon_id):
    query = "SELECT id_salon FROM Salon WHERE id_salon = %s AND FIND_IN_SET(%s, id_membre)"
    cursor.execute(query, (salon_id, user_id))
    result = cursor.fetchone()
    if result:
        return True
    return False
def get_user_id(cursor, username):
    query = "SELECT id_util FROM Utilisateur WHERE login = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None
def get_salon_id(cursor, salon_name):
    query = "SELECT id_salon FROM Salon WHERE nom_salon = %s"
    cursor.execute(query, (salon_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None
def get_salon_name(cursor, salon_id):
    query = "SELECT nom_salon FROM Salon WHERE id_salon = %s"
    cursor.execute(query, (salon_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None
def get_salon_members(cursor, salon_name):
    query = "SELECT id_membre FROM Salon WHERE nom_salon = %s"
    cursor.execute(query, (salon_name,))
    result = cursor.fetchone()
    if result:
        members_string = result[0]
        if members_string:
            return [int(member) for member in members_string.split(',')]
    return []
def get_user_name(cursor, user_id):
    query = "SELECT login FROM Utilisateur WHERE id_util = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return "Utilisateur Inconnu"
def salon(user_login, salon_name, salon_message):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            user_id = get_user_id(cursor, user_login)
            if user_id:
                salon_members = get_salon_members(cursor, salon_name)
                if user_id in salon_members:
                    tagged_message = f":{salon_name} {user_login}:{salon_message}"
                    db_connection.close()
                    return tagged_message
                else:
                    db_connection.close()
                    return "Vous n'êtes pas autorisé à envoyer des messages dans ce salon."

    except mysql.connector.Error as error:
        logs(f"Error: {error}")
        return "Une erreur s'est produite lors de la vérification du salon."
def sign_up(username, password):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            insert_query = "INSERT INTO Utilisateur (login, mdp, etat_util) VALUES (%s, %s, %s)"
            data = (username, password, "connect")
            cursor.execute(insert_query, data)

            user_id = get_user_id(cursor,username)
            update_query = "UPDATE Salon SET id_membre = CONCAT_WS(',', IFNULL(id_membre, ''), %s) WHERE nom_salon = 'general'"
            cursor.execute(update_query, (user_id,))

            db_connection.commit()
            db_connection.close()
            return True

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return False
def kill(admin_user, target_user, reason):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()
            admin_privilege = check_admin_privileges(cursor, admin_user)

            target_query = "SELECT etat_util FROM Utilisateur WHERE login = %s"
            cursor.execute(target_query, (target_user,))
            target_result = cursor.fetchone()

            if admin_privilege and target_result and target_result[0] == 'connect':
                target_user_id = get_user_id(cursor, target_user)
                if target_user_id:
                    insert_query = "INSERT INTO Killh (id_util, raison_kill, d_h_kill) VALUES (%s, %s, %s)"
                    data = (target_user_id, reason, datetime.now())
                    cursor.execute(insert_query, data)
                    db_connection.commit()
                    db_connection.close()
                    return True
                else:
                    logs(f"Utilisateur '{target_user}' non trouvé.")
            else:
                logs(f"{admin_user}:Permissions insuffisantes ou utilisateur non connecté.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return False
def ban(admin_user, ban_target, reason):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            admin_privilege = check_admin_privileges(cursor, admin_user)

            user_query = "SELECT id_util FROM Utilisateur WHERE login = %s"
            cursor.execute(user_query, (ban_target,))
            user_result = cursor.fetchone()

            ip_parts = ban_target.split('.')
            if len(ip_parts) == 4:
                valid_ip = all(0 <= int(part) < 255 for part in ip_parts)
                if valid_ip:
                    user_result = True

            if admin_privilege and user_result:
                if isinstance(user_result, tuple):
                    target_user_id = user_result[0]
                    ban_ip = None
                else:
                    target_user_id = None
                    ban_ip = ban_target

                insert_query = "INSERT INTO Ban (id_util, ban_ip, raison_ban, d_h_ban) VALUES (%s, %s, %s, %s)"
                data = (target_user_id, ban_ip, reason, datetime.now())
                cursor.execute(insert_query, data)
                db_connection.commit()
                db_connection.close()
                return True
            else:
                logs(f"{admin_user}:Utilisateur ou IP '{ban_target}' non trouvé ou format invalide.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return False
def kick(admin_user, target_user, duration_minutes, reason):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            admin_privilege = check_admin_privileges(cursor, admin_user)

            target_user_id = get_user_id(cursor, target_user)

            if admin_privilege and target_user_id:
                end_time = datetime.now() + timedelta(minutes=int(duration_minutes))

                insert_query = "INSERT INTO Kick (id_util, raison_kick, d_h_kick, fin_kick) VALUES (%s, %s, %s, %s)"
                data = (target_user_id, reason, datetime.now(), end_time)
                cursor.execute(insert_query, data)
                db_connection.commit()
                db_connection.close()
                return True
            else:
                logs(f"{admin_user}:Permissions insuffisantes ou utilisateur non trouvé.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return False
def demande(admin_user, type_demande, demande_text):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            user_id = get_user_id(cursor, admin_user)

            if user_id:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                insert_query = "INSERT INTO Demande (id_util, type_demande, d_h_demande, etat_demande, demande) VALUES (%s, %s, %s, %s, %s)"
                data = (user_id, type_demande, current_time, 'Nouveau', demande_text)
                cursor.execute(insert_query, data)
                db_connection.commit()
                db_connection.close()
                return True
            else:
                logs(f"{admin_user}: Utilisateur non trouvé pour créer la demande.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        logs(f"Error: {error}")
        return False
def admin_demande(admin_user, conn):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            if check_admin_privileges(cursor, admin_user):
                select_query = "SELECT * FROM Demande"
                cursor.execute(select_query)
                demande_results = cursor.fetchall()

                if demande_results:
                    demande_message = ": Demande: \n"
                    for demande in demande_results:
                        user_id = demande[2]
                        user_name = get_user_name(cursor,user_id)
                        demande_message += f"N°Demande:{demande[0]}       Utilisateur: {user_name}       Type: {demande[1]}       Demande:{demande[5]}       Le, à:{demande[3]}       Etat:{demande[4]}       Comentaire admin:{demande[6]} \n"
                    conn.send(demande_message.encode())
                else:
                    conn.send("Aucune demande enregistrée.".encode())

            else:
                conn.send("Vous n'avez pas les autorisations nécessaires pour cette commande.".encode())

            cursor.close()
            db_connection.close()
        else:
            conn.send("Impossible de se connecter à la base de données.".encode())

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        conn.send("Une erreur s'est produite lors de la récupération des demandes.".encode())
def admin_demande_salon(admin_user, conn):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            if check_admin_privileges(cursor, admin_user):
                select_query = "SELECT * FROM Demande_salon"
                cursor.execute(select_query)
                demande_salon_results = cursor.fetchall()

                if demande_salon_results:
                    demande_salon_message = ": Demande: \n"
                    for demande in demande_salon_results:
                        user_id = demande[1]
                        user_name = get_user_name(cursor,user_id)
                        salon_id = demande[2]
                        name_salon = get_salon_name(cursor, salon_id )
                        demande_salon_message += f"N°Demande:{demande[0]}       Utilisateur: {user_name}       Salon: {name_salon}       Raison: {demande[4]}       Etat: {demande[3]} \n"
                    conn.send(demande_salon_message.encode())
                else:
                    conn.send("Aucune demande de salon enregistrée.".encode())

            else:
                conn.send("Vous n'avez pas les autorisations nécessaires pour cette commande.".encode())

            cursor.close()
            db_connection.close()
        else:
            conn.send("Impossible de se connecter à la base de données.".encode())

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        conn.send("Une erreur s'est produite lors de la récupération des demandes.".encode())
def demande_salon_update(admin_user, id_demande_salon, etat_demande_salon):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            if check_admin_privileges(cursor, admin_user):
                select_query = "SELECT id_util, id_salon FROM Demande_salon WHERE id_dsalon = %s"
                cursor.execute(select_query, (id_demande_salon,))
                demande_salon_result = cursor.fetchone()
                if demande_salon_result:
                    if etat_demande_salon == "yes" :
                        update_query = "UPDATE Demande_salon SET etat_dsalon = %s WHERE id_dsalon = %s"
                        cursor.execute(update_query, (etat_demande_salon, id_demande_salon))
                        db_connection.commit()
                        user_id_dsalon = demande_salon_result[0]
                        salon_id = demande_salon_result[1]
                        if user_id_dsalon:
                            add_member_query = "UPDATE Salon SET id_membre = CONCAT(id_membre, %s) WHERE id_salon = %s"
                            cursor.execute(add_member_query, (f',{user_id_dsalon}', salon_id))
                            db_connection.commit()
                            db_connection.close()
                        return True
                    elif etat_demande_salon == "no":
                        update_query = "UPDATE Demande_salon SET etat_dsalon = %s WHERE id_dsalon = %s"
                        cursor.execute(update_query, (etat_demande_salon, id_demande_salon))
                        db_connection.commit()
                        db_connection.close()
                        return True
                    else:
                        logs(f"Demande avec un argument autre que yes ou ok")
                else:
                    logs(f"Demande avec l'ID {id_demande_salon} non trouvée.")
            else:
                logs(f"{admin_user}: Vous n'avez pas les autorisations nécessaires pour cette commande.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return False
def ticket(admin_user, id_demande, etat_demande, commentaire):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            if check_admin_privileges(cursor, admin_user):
                select_query = "SELECT etat_demande, commentaire FROM Demande WHERE id_demande = %s"
                cursor.execute(select_query, (id_demande,))
                demande_result = cursor.fetchone()

                if demande_result:
                    ancien_commentaire = demande_result[1]

                    new_commentaire = f"Admin :{admin_user}   Le, à: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}     Commentaire:{commentaire}"
                    if ancien_commentaire:
                        new_commentaire = f"{ancien_commentaire}; {new_commentaire}"

                    update_query = "UPDATE Demande SET etat_demande = %s, commentaire = %s WHERE id_demande = %s"
                    cursor.execute(update_query, (etat_demande, new_commentaire, id_demande))
                    db_connection.commit()

                    db_connection.close()
                    return True
                else:
                    logs(f"Demande avec l'ID {id_demande} non trouvée.")
            else:
                logs(f"{admin_user}: Vous n'avez pas les autorisations nécessaires pour cette commande.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return False
def liste_salons(user_id):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            query = "SELECT nom_salon, type_salon, id_membre FROM Salon"
            cursor.execute(query)
            result = cursor.fetchall()

            if result:
                salon_list = []
                for row in result:
                    nom_salon = row[0]
                    etat_salon = row[1]
                    membres = [int(member) for member in row[2].split(',') if member]

                    if user_id in membres:
                        salon_list.append(f"{nom_salon};{etat_salon};True")
                    else:
                        salon_list.append(f"{nom_salon};{etat_salon};False")

                db_connection.close()
                return "|".join(salon_list)
            else:
                db_connection.close()
                return "Aucun salon trouvé."

    except mysql.connector.Error as error:
        logs(f"Erreur lors de la récupération de la liste des salons : {error}")
        return "Une erreur s'est produite lors de la récupération de la liste des salons."
def liste_util(user_login):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            user_id = get_user_id(cursor, user_login)

            query = "SELECT login, etat_util FROM Utilisateur WHERE id_util != %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()

            if result:
                user_list = [f"{row[0]};{row[1]}" for row in result]
                db_connection.close()
                return "| ".join(user_list)
            else:
                db_connection.close()
                return "Aucun utilisateur trouvé."

    except mysql.connector.Error as error:
        logs(f"Erreur lors de la récupération de la liste des utilisateurs : {error}")
        return "Une erreur s'est produite lors de la récupération de la liste des utilisateurs."
def user_tickets(user_name):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            user_id = get_user_id(cursor, user_name)

            select_query = "SELECT * FROM Demande WHERE id_util = %s"
            cursor.execute(select_query, (user_id,))
            demandes = cursor.fetchall()

            user_tickets_message = ""
            if demandes:
                for demande in demandes:
                    demande_message = f":Demande : N°Demande:{demande[0]}       Type: {demande[1]}       Demande:{demande[5]}       Le, à:{demande[3]}       Etat:{demande[4]}       Comentaire admin:{demande[6]} \n"
                    user_tickets_message += demande_message

                db_connection.close()
                return user_tickets_message
            else:
                db_connection.close()
                return "Aucune demande trouvée pour cet utilisateur."

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return "Une erreur s'est produite lors de la récupération des demandes."
def demande_salon(user_login, salon_name, raison):
    try:
        db_connection = connect_to_db()

        if db_connection:
            cursor = db_connection.cursor()

            salon_query = "SELECT id_salon, type_salon FROM Salon WHERE nom_salon = %s"
            cursor.execute(salon_query, (salon_name,))
            salon_result = cursor.fetchone()
            print(salon_result)
            if salon_result:
                salon_id, salon_type = salon_result
                print(salon_id,salon_type)

                if salon_type == "open":
                    user_id = get_user_id(cursor, user_login)
                    if user_id:
                        add_member_query = "UPDATE Salon SET id_membre = CONCAT(id_membre, %s) WHERE id_salon = %s"
                        cursor.execute(add_member_query, (f',{user_id}', salon_id))
                        db_connection.commit()
                        db_connection.close()
                        return "open"
                elif salon_type == 'close':
                    if raison:
                        user_id = get_user_id(cursor, user_login)
                        if user_id:
                            demande_query = "INSERT INTO Demande_salon (id_util, id_salon, etat_dsalon, raison_dsalon) VALUES (%s, %s, %s, %s)"
                            cursor.execute(demande_query, (user_id, salon_id, 'attente', raison))
                            db_connection.commit()
                            db_connection.close()
                            return "closed"
                    else:
                        db_connection.close()
                        return "reason_required"

            db_connection.close()
            return "success"

    except mysql.connector.Error as error:
        logs(f"Error: {error}")
        return "failure"
def log_to_database(log_message):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            insert_query = "INSERT INTO Logs (logs, d_h_logs) VALUES (%s, %s)"
            data = (log_message, current_time)
            cursor.execute(insert_query, data)
            db_connection.commit()
            cursor.close()
            db_connection.close()
    except mysql.connector.Error as err:
        print(f"Erreur lors de l'insertion des logs dans la base de données : {err}")
def logs(message):
    print(message)
    log_to_database(message)