import mysql.connector
from administration import logs, check_admin_privileges,connect_to_db
"""
    Programe permetant l'identification des client
"""
def is_user_or_ip_banned(login, ip_address):
    """
    Vérifie si un utilisateur ou une adresse IP est banni.

    Args:
        login (str): Le nom d'utilisateur pour vérifier le statut de bannissement.
        ip_address (str): L'adresse IP pour vérifier le statut de bannissement.

    Returns:
        bool or tuple or None: Retourne True si l'utilisateur est banni par nom d'utilisateur ou par adresse IP,
        False s'il n'est pas banni. Si l'utilisateur a une entrée dans la table Kick avec une expulsion active,
        renvoie un tuple ou None selon la situation.

    Notes:
        Cette fonction interroge la base de données pour vérifier si l'utilisateur ou l'adresse IP est banni.
        Elle recherche d'abord dans la table de bannissement par nom d'utilisateur, puis par adresse IP.
        Enfin, elle vérifie la table des Kick pour voir si l'utilisateur a une expulsion active.
        Elle retourne des valeurs booléennes ou un tuple en fonction de la situation de bannissement de l'utilisateur.
    """
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()


            user_ban_query = "SELECT id_util FROM Ban WHERE id_util = (SELECT id_util FROM Utilisateur WHERE login = %s)"
            cursor.execute(user_ban_query, (login,))
            user_ban = cursor.fetchone()


            ip_ban_query = "SELECT ban_ip FROM Ban WHERE ban_ip = %s"
            cursor.execute(ip_ban_query, (ip_address,))
            ip_ban = cursor.fetchone()


            kick_query = "SELECT id_kick FROM Kick WHERE id_util = (SELECT id_util FROM Utilisateur WHERE login = %s) AND fin_kick > NOW()"
            cursor.execute(kick_query, (login,))
            kick_entry = cursor.fetchone()

            db_connection.close()

            return user_ban or ip_ban or kick_entry

    except mysql.connector.Error as error:
        logs(f"Error:, {error}")
        return True
def connection(message, ip_address):
    """
    Gère la connexion d'un utilisateur et effectue les vérifications nécessaires.

    Args:
        message (str): Le message de connexion envoyé par l'utilisateur.
        ip_address (str): L'adresse IP de l'utilisateur.

    Returns:
        str or False: Retourne 'admin' si l'utilisateur est un administrateur et connecté avec succès,
        'co' s'il est connecté avec succès en tant qu'utilisateur normal, False sinon.

    Notes:
        Cette fonction traite la demande de connexion d'un utilisateur en vérifiant le format du message,
        puis en vérifiant si l'utilisateur est banni ou kické en utilisant la fonction is_user_or_ip_banned.
        Elle tente ensuite de se connecter à la base de données et vérifie les informations d'identification de l'utilisateur.
        Si les informations sont valides, elle met à jour l'adresse IP de l'utilisateur et son état de connexion.
        Elle renvoie le statut de l'utilisateur ('admin' ou 'co') en cas de succès ou False en cas d'échec.
    """
    msg_split = message.split()
    if len(msg_split) != 3 or msg_split[0] != '/connect':
        return False

    login = msg_split[1]
    mdp = msg_split[2]

    if is_user_or_ip_banned(login, ip_address):
        logs(f"{login} est banni ou kické mais ne veut pas l'admettre")
        return False

    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            query = "SELECT * FROM Utilisateur WHERE login = %s AND mdp = %s"
            cursor.execute(query, (login, mdp))
            user = cursor.fetchone()

            if user:
                update_query = "UPDATE Utilisateur SET last_ip = %s, etat_util = 'connect' WHERE login = %s"
                cursor.execute(update_query, (ip_address, login))
                db_connection.commit()

                if check_admin_privileges(cursor, login):
                    return "admin"
                else:
                    return "co"

                db_connection.close()
            db_connection.close()
            return False

    except mysql.connector.Error as error:
        logs(f"Error: {error}")
        return False
def main():
    msg = "/connect toto toto"
    ip = "192.168.1.4"

    result = connection(msg, ip)
    print(result)
if __name__ == "__main__":
    main()
