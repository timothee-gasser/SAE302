import mysql.connector
from datetime import datetime

def get_user_id(cursor, username):
    query = "SELECT id_util FROM Utilisateur WHERE login = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def kill(admin_user, target_user, reason):
    try:
        db_connection = mysql.connector.connect(
            host='192.168.0.6',
            user='toto',
            password='toto',
            database='SAE302'
        )

        cursor = db_connection.cursor()

        # Vérifier les autorisations de l'admin
        admin_query = "SELECT type_util FROM Utilisateur WHERE login = %s"
        cursor.execute(admin_query, (admin_user,))
        admin_result = cursor.fetchone()

        # Vérifier si l'utilisateur à supprimer est connecté
        target_query = "SELECT etat_util FROM Utilisateur WHERE login = %s"
        cursor.execute(target_query, (target_user,))
        target_result = cursor.fetchone()

        if admin_result and admin_result[0] == 'admin' and target_result and target_result[0] == 'connect':
            # Obtenir l'ID de l'utilisateur cible
            target_user_id = get_user_id(cursor, target_user)
            if target_user_id:
                # Insérer les informations dans la table Killh
                insert_query = "INSERT INTO Killh (id_util, raison_kill, d_h_kill) VALUES (%s, %s, %s)"
                data = (target_user_id, reason, datetime.now())
                cursor.execute(insert_query, data)
                db_connection.commit()

                db_connection.close()
                return True
            else:
                print(f"Utilisateur '{target_user}' non trouvé.")
                db_connection.close()
                return False
        else:
            db_connection.close()
            return False

    except mysql.connector.Error as error:
        print("Error:", error)
        return False
