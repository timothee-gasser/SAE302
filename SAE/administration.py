# administration.py

import mysql.connector

def kill(admin_user, target_user):
    try:
        # Connecter à la base de données
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
            db_connection.close()
            return True
        else:
            db_connection.close()
            return False

    except mysql.connector.Error as error:
        print("Error:", error)
        return False
