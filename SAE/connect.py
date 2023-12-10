import mysql.connector

def connection(message, ip_address):
    msg_split = message.split()
    if len(msg_split) != 3 or msg_split[0] != '/connect':
        return False

    login = msg_split[1]
    mdp = msg_split[2]
    try:
        db_connection = mysql.connector.connect(
            host='192.168.0.14',
            user='toto',
            password='toto',
            database='SAE302'
        )
        cursor = db_connection.cursor()
        query = "SELECT * FROM Utilisateur WHERE login = %s AND mdp = %s"
        cursor.execute(query, (login, mdp))
        user = cursor.fetchone()

        if user:
            update_query = "UPDATE Utilisateur SET last_ip = %s WHERE login = %s"
            cursor.execute(update_query, (ip_address, login))
            db_connection.commit()
            db_connection.close()
            return True

        db_connection.close()
        return False

    except mysql.connector.Error as error:
        print("Error:", error)
        return False




def main():

    msg = "/connect titi titi"
    ip = "192.168.1.3"

    result = connection(msg, ip)
    print(result)

if __name__ == "__main__":
    main()

