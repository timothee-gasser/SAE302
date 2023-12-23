import mysql.connector
from datetime import datetime, timedelta


def connect_to_db():
    try:
        db_connection = mysql.connector.connect(
            host='192.168.0.6',
            user='toto',
            password='toto',
            database='SAE302'
        )
        return db_connection
    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return None

# Fonction pour vérifier les autorisations de l'admin
def check_admin_privileges(cursor, admin_user):
    admin_query = "SELECT type_util FROM Utilisateur WHERE login = %s"
    cursor.execute(admin_query, (admin_user,))
    admin_result = cursor.fetchone()
    if admin_result and admin_result[0] == 'admin':
        return True
    return False

def get_user_id(cursor, username):
    query = "SELECT id_util FROM Utilisateur WHERE login = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def get_user_name(cursor, user_id):
    query = "SELECT login FROM Utilisateur WHERE id_util = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return "Utilisateur Inconnu"


def kill(admin_user, target_user, reason):
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            # Vérifier les autorisations de l'admin
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
                    ancien_etat = demande_result[0]
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
                    demande_message = f":Demande : N°Demande:{demande[0]}       Utilisateur: {user_name}       Type: {demande[1]}       Demande:{demande[5]}       Le, à:{demande[3]}       Etat:{demande[4]}       Comentaire admin:{demande[6]} \n"
                    user_tickets_message += demande_message

                db_connection.close()
                return user_tickets_message
            else:
                db_connection.close()
                return "Aucune demande trouvée pour cet utilisateur."

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return "Une erreur s'est produite lors de la récupération des demandes."




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