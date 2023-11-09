import socket

host = '0.0.0.0'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print(f"Le serveur écoute sur {host}:{port}")

while True:
    conn, address = server_socket.accept()
    print(f"Connexion entrante de {address}")

    try:
        while True:
            data = conn.recv(1024).decode()

            if not data:
                print(f" Le client {address} c'est barré")
                break

            if data.lower() == 'bye':
                bye = "ok bye"
                conn.send(bye.encode())
                print(f"Le client {address} s'est deco")
                break

            if data.lower() == 'arret':
                arret = "ok arret"
                conn.send(arret.encode())
                server_socket.close()
                print("Arrêt du serveur")
                break

            response = "bien recu"
            conn.send(response.encode())
            print(f"Message du client : {data}")

    except ConnectionResetError:
        print(f"Le client {address} a fait de la merde")

    conn.close()

    if data.lower() == 'arret':
        break
