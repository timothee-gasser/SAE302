import socket
import threading

def srv(conn, address):
    try:
        serveur_en_marche = True

        while serveur_en_marche:
            try:
                data = conn.recv(1024).decode()

                if not data:
                    print(f"Le client {address} s'est déconnecté")
                    break

                if data.lower() == 'bye':
                    bye = "ok bye"
                    conn.send(bye.encode())
                    print(f"Le client {address} s'est déconnecté")
                    serveur_en_marche = True
                    conn.close()
                    print(f"Le serveur écoute sur {host}:{port}")
                    conn, address = server_socket.accept()

                elif data.lower() == 'arret':
                    arret = "ok arret"
                    conn.send(arret.encode())
                    print(f"Arrêt du serveur demandé par le client {address}")
                    serveur_en_marche = False
                    conn.close()
                    print("Arrêt du serveur")
                else:
                    response = "bien recu"
                    conn.send(response.encode())
                    print(f"Message du client : {data}")

            except Exception as e:
                print(f"Une erreur s'est produite : {e}")

    except Exception as e:
        print(f"Erreur lors de la création du serveur : {e}")

    finally:
        server_socket.close()
if __name__ == '__main__':
    host = '0.0.0.0'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Le serveur écoute sur {host}:{port}")
    conn, address = server_socket.accept()
    print(f"Connexion entrante de {address}")
    t1 = threading.Thread(target=srv(conn,address))
    t1.start()
    print('aaaaaaaaaaaaaa')
    while True:
        message = input("Ton message : ")
        server_socket.send(message)
    t1.join()