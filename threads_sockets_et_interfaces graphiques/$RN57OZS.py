import socket

host = '0.0.0.0'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print(f"Le serveur écoute sur {host}:{port}")

try:
    def srv():
        while True:
            conn, address = server_socket.accept()
            print(f"Connexion entrante de {conn}")
            while True:
                data = conn.recv(1024).decode()

                if data.lower() == 'bye':
                    bye = "ok bye"
                    conn.send(bye.encode())
                    print(f"Le client {conn} c'est deco")
                    break

                if data.lower() == 'arret':
                    arret = "ok arret"
                    conn.send(arret.encode())
                    server_socket.close()
                    print("arret du srv")
                    break
                response = "bien recu"
                conn.send(response.encode())
                print(f"Message du client : {data}")
            conn.close()
            if data.lower() == 'arret':
                break
except ConnectionAbortedError:
    print("Le client a fait de la merde")
except ConnectionResetError:
    print("Le client a fait de la merde")
finally:
    srv()