import socket
import time
from mathfunct import ln

host = '0.0.0.0'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv_marche = True
server_socket.bind((host, port))
while srv_marche:

    server_socket.listen(1)
    print(f"Le serveur écoute sur {host}:{port}")

    conn, address = server_socket.accept()
    print(f"Connexion entrante de {address}")

    data1 = conn.recv(1024).decode()
    print(f"Message du client : {data1}")
    if data1.lower() == 'arret':
        arret = "ok arret"
        conn.send(arret.encode())
        print(f"Arrêt du serveur demandé par le client {address}")
        conn.close()
        print("Arrêt du serveur")
        srv_marche = False
    elif data1.lower() == "ln":
        try:
            data2 = float(conn.recv(1024).decode())
            print(f"Message du client : {data2}")
            res_ln = ln(data2)
            response = f"Ln({data2}) = {res_ln}"
            conn.send(response.encode())
            print(response)
            time.sleep(1)
        except ValueError as e:
            error_msg = f"Erreur : {e}"
            conn.send(error_msg.encode())
            print(error_msg)
            time.sleep(1)
    else:
        data2 = conn.recv(1024).decode()
        print(f"Message du client : {data2}")
        response = "Aucune action n'a été effectuée car le premier message n'était pas 'ln'"
        conn.send(response.encode())
        time.sleep(1)

server_socket.close()
