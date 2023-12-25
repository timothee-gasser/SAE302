import mysql.connector
from datetime import datetime
from administration import logs
def is_user_or_ip_banned(login, ip_address):
    try:
        db_connection = mysql.connector.connect(
            host="185.39.142.44",
            port="3333",
            user='toto',
            password='toto',
            database='SAE302'
        )
        cursor = db_connection.cursor()

        # Vérification du ban par nom d'utilisateur
        user_ban_query = "SELECT id_util FROM Ban WHERE id_util = (SELECT id_util FROM Utilisateur WHERE login = %s)"
        cursor.execute(user_ban_query, (login,))
        user_ban = cursor.fetchone()

        # Vérification du ban par adresse IP
        ip_ban_query = "SELECT ban_ip FROM Ban WHERE ban_ip = %s"
        cursor.execute(ip_ban_query, (ip_address,))
        ip_ban = cursor.fetchone()

        # Vérification de la table Kick
        kick_query = "SELECT id_kick FROM Kick WHERE id_util = (SELECT id_util FROM Utilisateur WHERE login = %s) AND fin_kick > NOW()"
        cursor.execute(kick_query, (login,))
        kick_entry = cursor.fetchone()

        db_connection.close()

        return user_ban or ip_ban or kick_entry

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return True
def connection(message, ip_address):
    msg_split = message.split()
    if len(msg_split) != 3 or msg_split[0] != '/connect':
        return False

    login = msg_split[1]
    mdp = msg_split[2]

    if is_user_or_ip_banned(login, ip_address):
        logs(f"{login}le mec est ban ou kick mais y veux pas l'admaitre")
        return False

    try:
        db_connection = mysql.connector.connect(
            host="185.39.142.44",
            port="3333",
            user='toto',
            password='toto',
            database='SAE302'
        )
        cursor = db_connection.cursor()
        query = "SELECT * FROM Utilisateur WHERE login = %s AND mdp = %s"
        cursor.execute(query, (login, mdp))
        user = cursor.fetchone()

        if user:
            update_query = "UPDATE Utilisateur SET last_ip = %s, etat_util = 'connect' WHERE login = %s"
            cursor.execute(update_query, (ip_address, login))
            db_connection.commit()
            db_connection.close()
            return True

        db_connection.close()
        return False

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return False
def main():
    msg = "/connect ban_ip toto"
    ip = "192.168.1.4"

    result = connection(msg, ip)
    print(result)
if __name__ == "__main__":
    main()
