import mysql.connector
from datetime import datetime

# Fonction pour établir la connexion à la base de données
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
        print("Error:", error)
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
                    print(f"Utilisateur '{target_user}' non trouvé.")
            else:
                print("Permissions insuffisantes ou utilisateur non connecté.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        print("Error:", error)
        return False

def ban(admin_user, ban_target, reason, sender_name):
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

                insert_query = "INSERT INTO Ban (id_util, ban_ip, raison_ban, d_h_ban,) VALUES (%s, %s, %s, %s)"
                data = (target_user_id, ban_ip, reason, datetime.now())
                cursor.execute(insert_query, data)
                db_connection.commit()
                db_connection.close()
                return True
            else:
                print(f"Utilisateur ou IP '{ban_target}' non trouvé ou format invalide.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        print("Error:", error)
        return False
