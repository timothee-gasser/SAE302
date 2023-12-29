import mysql.connector
from datetime import datetime, timedelta
"""
Programe utiliser pour toutes les commende spécifique.
"""
def connect_to_db():
    """
        Établit une connexion à la base de données.

        Notes:
            Cette fonction établir une connexion à la base de données avec les informations d'identification spécifiées.
            Si la connexion réussit, elle renvoie l'objet de connexion.
            !!!!! Ne pas oublier d'adapter les information de la base de données !!!!!
        """
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
    """
    Vérifie les privilèges administratifs d'un utilisateur dans la base de données.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Le curseur de la base de données.
        admin_user (str): Le nom d'utilisateur de l'administrateur à vérifier.

    Returns:
        bool: True si l'utilisateur a des privilèges administratifs, sinon False.

    Notes:
        Cette fonction interroge la base de données pour vérifier si l'utilisateur spécifié a des privilèges
        administrateur. Elle exécute une requête SQL pour récupérer le type d'utilisateur. Si l'utilisateur est un
        administrateur ('admin'), elle renvoie True, sinon elle renvoie False.
    """
    admin_query = "SELECT type_util FROM Utilisateur WHERE login = %s"
    cursor.execute(admin_query, (admin_user,))
    admin_result = cursor.fetchone()
    if admin_result and admin_result[0] == 'admin':
        return True
    return False
def check_user_in_salon(cursor, user_id, salon_id):
    """
        Vérifie si un utilisateur est présent dans un salon donné.

        Args:
            cursor (mysql.connector.cursor.MySQLCursor): Le curseur de la base de données.
            user_id (int): L'identifiant de l'utilisateur à vérifier.
            salon_id (int): L'identifiant du salon dans lequel vérifier la présence de l'utilisateur.

        Returns:
            bool: True si l'utilisateur est présent dans le salon, sinon False.

        Notes:
            Cette fonction exécute une requête SQL pour vérifier si l'identifiant de l'utilisateur existe dans la liste des
            membres du salon spécifié. Si l'utilisateur est présent dans le salon, la fonction renvoie True, sinon elle
            renvoie False.
        """
    query = "SELECT id_salon FROM Salon WHERE id_salon = %s AND FIND_IN_SET(%s, id_membre)"
    cursor.execute(query, (salon_id, user_id))
    result = cursor.fetchone()
    if result:
        return True
    return False
def get_user_id(cursor, username):
    """
        Récupère l'identifiant d'un utilisateur à partir de son nom d'utilisateur.

        Args:
            cursor (mysql.connector.cursor.MySQLCursor): Le curseur de la base de données.
            username (str): Le nom d'utilisateur pour lequel récupérer l'identifiant.

        Returns:
            int or None: L'identifiant de l'utilisateur s'il est trouvé, None sinon.

        Notes:
            Cette fonction exécute une requête SQL pour récupérer l'identifiant de l'utilisateur en fonction de son nom
            d'utilisateur. Si un résultat est trouvé dans la base de données, la fonction renvoie l'identifiant de
            l'utilisateur, sinon elle renvoie None.
        """
    query = "SELECT id_util FROM Utilisateur WHERE login = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None
def get_salon_id(cursor, salon_name):
    """
    Récupère l'identifiant d'un salon à partir de son nom.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Le curseur de la base de données.
        salon_name (str): Le nom du salon pour lequel récupérer l'identifiant.

    Returns:
        int or None: L'identifiant du salon s'il est trouvé, None sinon.

    Notes:
        Cette fonction exécute une requête SQL pour récupérer l'identifiant du salon en fonction de son nom.
        Si un résultat est trouvé dans la base de données, la fonction renvoie l'identifiant du salon,
        sinon elle renvoie None.
    """
    query = "SELECT id_salon FROM Salon WHERE nom_salon = %s"
    cursor.execute(query, (salon_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None
def get_salon_name(cursor, salon_id):
    """
    Récupère le nom d'un salon à partir de son identifiant.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Le curseur de la base de données.
        salon_id (int): L'identifiant du salon pour lequel récupérer le nom.

    Returns:
        str or None: Le nom du salon s'il est trouvé, None sinon.

    Notes:
        Cette fonction exécute une requête SQL pour récupérer le nom du salon en fonction de son identifiant.
        Si un résultat est trouvé dans la base de données, la fonction renvoie le nom du salon,
        sinon elle renvoie None.
    """
    query = "SELECT nom_salon FROM Salon WHERE id_salon = %s"
    cursor.execute(query, (salon_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None
def get_salon_members(cursor, salon_name):
    """
        Récupère les membres d'un salon à partir de son nom.

        Args:
            cursor (mysql.connector.cursor.MySQLCursor): Le curseur de la base de données.
            salon_name (str): Le nom du salon pour lequel récupérer les membres.

        Returns:
            list: Une liste des identifiants des membres du salon, vide si aucun membre n'est trouvé.

        Notes:
            Cette fonction exécute une requête SQL pour récupérer les identifiants des membres du salon en fonction
            de son nom. Elle renvoie une liste des identifiants des membres sous forme d'entiers.
            Si aucun membre n'est trouvé dans la base de données, la fonction renvoie une liste vide.
        """
    query = "SELECT id_membre FROM Salon WHERE nom_salon = %s"
    cursor.execute(query, (salon_name,))
    result = cursor.fetchone()
    if result:
        members_string = result[0]
        if members_string:
            return [int(member) for member in members_string.split(',')]
    return []
def get_user_name(cursor, user_id):
    """
        Récupère le nom d'utilisateur à partir de son identifiant.

        Args:
            cursor (mysql.connector.cursor.MySQLCursor): Le curseur de la base de données.
            user_id (int): L'identifiant de l'utilisateur pour lequel récupérer le nom.

        Returns:
            str: Le nom de l'utilisateur s'il est trouvé, sinon "Utilisateur Inconnu".

        Notes:
            Cette fonction exécute une requête SQL pour récupérer le nom de l'utilisateur en fonction de son identifiant.
            Si un résultat est trouvé dans la base de données, la fonction renvoie le nom de l'utilisateur,
            sinon elle renvoie "Utilisateur Inconnu".
        """

    query = "SELECT login FROM Utilisateur WHERE id_util = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return "Utilisateur Inconnu"
def salon(user_login, salon_name, salon_message):
    """
        Vérifie les autorisations et forme le message pour un salon.

        Args:
            user_login (str): Le nom d'utilisateur envoyant le message.
            salon_name (str): Le nom du salon où envoyer le message.
            salon_message (str): Le message à envoyer dans le salon.

        Returns:
            str: Le message formaté avec les tags du salon s'il est autorisé à envoyer des messages dans le salon,
                 sinon un message indiquant l'absence d'autorisation.

        Notes:
            Cette fonction vérifie si l'utilisateur a l'autorisation d'envoyer des messages dans un salon spécifié.
            Si l'utilisateur est autorisé, la fonction forme le message avec les tags du salon et le nom d'utilisateur,
            sinon elle renvoie un message indiquant l'absence d'autorisation pour envoyer des messages dans ce salon.
        """
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
    """
        Enregistre un nouvel utilisateur dans la base de données.

        Args:
            username (str): Le nom d'utilisateur pour le nouveau compte.
            password (str): Le mot de passe associé au compte.

        Returns:
            bool: True si l'inscription a réussi, False sinon.

        Notes:
            Cette fonction enregistre un nouvel utilisateur avec un nom d'utilisateur et un mot de passe donnés.
            Elle crée également une entrée pour l'utilisateur dans le salon général après l'inscription.
        """
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
    """
        Mettre fin à une session utilisateur en documentant dans la base de données.

        Args:
            admin_user (str): L'administrateur effectuant l'action de suppression.
            target_user (str): L'utilisateur à terminer.
            reason (str): La raison fournie pour la suppression.

        Returns:
            bool: True si l'action de suppression a réussi, False sinon.
        """
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
    """
    Bannit un utilisateur ou une adresse IP.

    Args:
        admin_user (str): Nom de l'administrateur effectuant le bannissement.
        ban_target (str): Nom d'utilisateur ou adresse IP à bannir.
        reason (str): Raison du bannissement.

    Returns:
        bool: True si le bannissement est effectué avec succès, False sinon.

    Notes:
        Cette fonction bannit un utilisateur ou une adresse IP spécifiée pour une raison donnée.
        Elle vérifie les privilèges de l'administrateur et la validité de l'utilisateur ou de l'adresse IP ciblée.
        Si le bannissement est réussi, un enregistrement est créé dans la base de données.
    """
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
    """
        Kick un utilisateur pour une durée spécifiée.

        Args:
            admin_user (str): Nom de l'administrateur effectuant l'exclusion.
            target_user (str): Nom de l'utilisateur à exclure.
            duration_minutes (int): Durée de l'exclusion en minutes.
            reason (str): Raison de l'exclusion.

        Returns:
            bool: True si l'exclusion est effectuée avec succès, False sinon.

        Notes:
            Cette fonction kick un utilisateur spécifié pour une durée donnée avec une raison donnée.
            Elle vérifie les privilèges de l'administrateur et l'existence de l'utilisateur ciblé.
            Si l'exclusion est réussie, un enregistrement est créé dans la base de données.
        """
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
def demande(user, type_demande, demande_text):
    """
        Enregistre une nouvelle demande dans la base de données.

        Args:
            user (str): Nom de l'utilisateur créant la demande.
            type_demande (str): Type de la demande.
            demande_text (str): Texte de la demande.

        Returns:
            bool: True si l'enregistrement de la demande est effectué avec succès, False sinon.

        Notes:
            Cette fonction crée une nouvelle demande associée à un utilisateur spécifié avec un type
            de demande et un texte donnés.
        """
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            user_id = get_user_id(cursor, user)

            if user_id:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                insert_query = "INSERT INTO Demande (id_util, type_demande, d_h_demande, etat_demande, demande) VALUES (%s, %s, %s, %s, %s)"
                data = (user_id, type_demande, current_time, 'Nouveau', demande_text)
                cursor.execute(insert_query, data)
                db_connection.commit()
                db_connection.close()
                return True
            else:
                logs(f"{user}: Utilisateur non trouvé pour créer la demande.")

            db_connection.close()
            return False

    except mysql.connector.Error as error:
        logs(f"Error: {error}")
        return False
def admin_demande(admin_user, conn):
    """
        Récupère les demandes et les envoie au client connecté.

        Args:
            admin_user (str): Nom de l'administrateur demandant les informations des demandes.
            conn: Objet de connexion au client.

        Notes:
            Cette fonction vérifie d'abord les privilèges administratifs de l'utilisateur. Si l'administrateur
            possède les privilèges requis, elle récupère les informations de toutes les demandes enregistrées
            dans la base de données et les envoie au client connecté. Sinon, elle envoie un message indiquant que
            l'utilisateur n'a pas les autorisations nécessaires.
        """
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
    """
        Récupère les demandes de salon et les envoie au client connecté.

        Args:
            admin_user (str): Nom de l'administrateur demandant les informations des demandes de salon.
            conn: Objet de connexion au client.

        Notes:
            Cette fonction vérifie d'abord les privilèges administratifs de l'utilisateur. Si l'administrateur
            possède les privilèges requis, elle récupère les informations de toutes les demandes de salon
            enregistrées dans la base de données et les envoie au client connecté. Sinon, elle envoie un message
            indiquant que l'utilisateur n'a pas les autorisations nécessaires.
        """
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
    """
        Met à jour l'état d'une demande de salon dans la base de données.

        Args:
            admin_user (str): Le nom de l'administrateur effectuant la mise à jour.
            id_demande_salon (int): L'identifiant de la demande de salon à mettre à jour.
            etat_demande_salon (str): L'état à assigner à la demande de salon ("yes" pour accepter, "no" pour refuser).

        Returns:
            bool: True si la mise à jour a réussi, False sinon.

        Notes:
            Cette fonction vérifie les privilèges administratifs de l'utilisateur. Si l'administrateur a les privilèges,
            elle met à jour l'état de la demande de salon correspondant à l'ID donné. Si l'état est "yes", elle met à jour
            la base de données avec cet état, ajoute l'utilisateur associé au salon spécifié, puis ferme la connexion.
            Si l'état est "no", elle met simplement à jour l'état de la demande de salon dans la base de données.
            Si l'argument `etat_demande_salon` n'est ni "yes" ni "no", un message d'erreur est enregistré dans les logs.
        """
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
    """
        Met à jour l'état et le commentaire d'une demande dans la base de données.

        Args:
            admin_user (str): Le nom de l'administrateur effectuant la mise à jour.
            id_demande (int): L'identifiant de la demande à mettre à jour.
            etat_demande (str): Le nouvel état de la demande.
            commentaire (str): Le commentaire à ajouter à la demande.

        Returns:
            bool: True si la mise à jour a réussi, False sinon.

        Notes:
            Cette fonction vérifie les privilèges administratifs de l'utilisateur. Si l'administrateur a les privilèges,
            elle récupère l'état actuel et le commentaire de la demande correspondant à l'ID donné. Ensuite, elle met à jour
            cet état avec la nouvelle valeur fournie et ajoute un commentaire à celui déjà existant (s'il y en a un).
            Elle met à jour la base de données avec ces nouvelles informations. Si aucune demande n'est trouvée avec l'ID donné,
            un message d'erreur est enregistré dans les logs.
        """
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
    """
        Récupère la liste des salons disponibles pour un utilisateur donné.

        Args:
            user_id (int): L'identifiant de l'utilisateur pour lequel récupérer la liste des salons.

        Returns:
            str: Une chaîne de caractères représentant la liste des salons disponibles pour l'utilisateur.

        Notes:
            Cette fonction interroge la base de données pour récupérer les informations sur tous les salons.
            Elle vérifie si l'utilisateur est membre de chaque salon en comparant son ID avec les membres associés
            à chaque salon. Si l'utilisateur est membre d'un salon, le salon est marqué comme disponible pour lui
            dans la liste retournée. La fonction retourne une chaîne de caractères représentant la liste des salons
            au format 'nom_salon;type_salon;True/False', où 'True' indique que l'utilisateur est membre du salon
            et 'False' indique le contraire. En cas d'erreur lors de la récupération des salons, un message d'erreur
            est renvoyé.
        """
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
    """
        Récupère la liste des autres utilisateurs enregistrés dans le système.

        Args:
            user_login (str): Le nom d'utilisateur pour lequel récupérer la liste des autres utilisateurs.

        Returns:
            str: Une chaîne de caractères représentant la liste des autres utilisateurs enregistrés.

        Notes:
            Cette fonction interroge la base de données pour obtenir les noms et les états des autres utilisateurs
            enregistrés, à l'exception de l'utilisateur dont le nom est spécifié. Elle retourne une chaîne de caractères
            contenant les noms d'utilisateur et leurs états, au format 'nom_utilisateur;etat_utilisateur'. Si aucun
            autre utilisateur n'est trouvé ou s'il y a une erreur lors de la récupération des données, un message
            d'erreur est renvoyé.
        """
    try:
        db_connection = connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            user_id = get_user_id(cursor, user_login)

            query = "SELECT login, etat_util FROM Utilisateur WHERE id_util != %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()

            if result:
                user_list = [f" {row[0]};{row[1]}" for row in result]
                db_connection.close()
                return "| ".join(user_list)
            else:
                db_connection.close()
                return "Aucun utilisateur trouvé."

    except mysql.connector.Error as error:
        logs(f"Erreur lors de la récupération de la liste des utilisateurs : {error}")
        return "Une erreur s'est produite lors de la récupération de la liste des utilisateurs."
def user_tickets(user_name):
    """
        Récupère les demandes associées à un utilisateur spécifique.

        Args:
            user_name (str): Le nom de l'utilisateur pour lequel récupérer les demandes.

        Returns:
            str: Une chaîne de caractères représentant les demandes associées à l'utilisateur.

        Notes:
            Cette fonction interroge la base de données pour récupérer les demandes enregistrées pour un utilisateur
            spécifié. Elle retourne une chaîne de caractères contenant les détails des demandes associées à l'utilisateur,
            au format 'N°Demande:ID_Demande;Type:Type_demande;Demande:Texte_demande;Le, à:Date_heure;Etat:Etat_demande;
            Comentaire admin:Commentaire_admin'. Si aucune demande n'est trouvée pour l'utilisateur ou s'il y a une erreur
            lors de la récupération des données, un message indiquant l'absence de demande est renvoyé.
        """
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
                    demande_message = f":Demande : N°Demande:{demande[0]};Type: {demande[1]};Demande:{demande[5]};Le, à:{demande[3]};Etat:{demande[4]};Comentaire admin:{demande[6]} \n"
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
    """
        Traite la demande d'adhésion à un salon et la demande de création de salon fermé.

        Args:
            user_login (str): Le nom de l'utilisateur faisant la demande.
            salon_name (str): Le nom du salon auquel l'utilisateur veut adhérer ou qu'il souhaite créer.
            raison (str): La raison fournie pour adhérer au salon fermé, requis s'il s'agit d'un salon fermé.

        Returns:
            str: Un message indiquant le résultat de la demande :
                - 'open' si l'utilisateur a été ajouté à un salon ouvert avec succès.
                - 'closed' si une demande pour un salon fermé a été enregistrée avec succès.
                - 'reason_required' si la raison est nécessaire pour la demande de salon fermé.
                - 'success' si aucune action spécifique n'est requise.
                - 'failure' en cas d'erreur lors du traitement de la demande.

        Notes:
            Cette fonction gère deux scénarios :
            1. Pour un salon ouvert ('open'), elle ajoute directement l'utilisateur au salon s'il existe.
            2. Pour un salon fermé ('close'), elle enregistre une demande avec la raison fournie.
               Si la raison est absente pour un salon fermé, elle indique que la raison est requise pour la demande.
            Elle retourne un message indiquant le résultat de la demande en fonction du scénario rencontré.
        """
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
    """
        Enregistre un message de journalisation dans la base de données.

        Args:
            log_message (str): Le message à enregistrer dans les journaux.

        Notes:
            Cette fonction insère le message de journalisation avec la date et l'heure actuelles dans la base de données.
            Elle permet de stocker des messages de journalisation pour des événements spécifiques ou des erreurs survenus.
        """
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
    """
        Affiche un message et enregistre ce message dans la base de données de journalisation.

        Args:
            message (str): Le message à afficher et à enregistrer.
            !!! Attention ne pas donner des suite de variable comme d'abitude avec un print. Il faut maitre sous forme f"{variable1}{variable2}" !!!

        Notes:
            Cette fonction imprime le message sur la sortie standard et enregistre également ce message dans la base de données de logs.
            Elle est utilisée pour afficher des messages dans la console et pour enregistrer des événements dans les logs de la base de données.

        """

    print(message)
    log_to_database(message)