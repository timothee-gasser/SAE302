import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QMessageBox,QTabWidget

class ConnectionDetails:
    def __init__(self, host, port, username, password, client_socket):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_socket = client_socket

class AdminWindow(QMainWindow):
    def __init__(self, connection_details):
        super().__init__()

        self.setWindowTitle("Fenêtre Admin")
        self.connection_details = connection_details

        layout = QVBoxLayout()

        self.received_messages = QTextEdit()
        self.received_messages.setReadOnly(True)
        layout.addWidget(self.received_messages)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        send_button = QPushButton("Envoyer")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        quit_button = QPushButton("Quitter")
        quit_button.clicked.connect(self.quit_app)
        layout.addWidget(quit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        try:
            self.received_messages.append(f"Connecté au serveur sur {self.connection_details.host}:{self.connection_details.port}")

            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la connexion : {e}")
            self.close()

    def receive_messages(self):
        while True:
            try:
                reply = self.connection_details.client_socket.recv(1024).decode()
                if not reply:
                    self.received_messages.append("Le serveur s'est déconnecté")
                    self.quit_app()
                    break
                self.received_messages.append(reply)

            except Exception as e:
                self.received_messages.append(f"Une erreur s'est produite lors de la réception des messages : {e}")
                self.quit_app()
                break

    def send_message(self):
        message = self.input_field.text()
        try:
            self.connection_details.client_socket.send(message.encode())
            self.input_field.clear()

        except Exception as e:
            self.received_messages.append(f"Une erreur s'est produite : {e}")

    def quit_app(self):
        self.connection_details.client_socket.send("bye".encode())
        self.connection_details.client_socket.close()
        QApplication.quit()

    def closeEvent(self, event):
        self.quit_app()

class ConnectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Connexion au serveur")

        layout = QVBoxLayout()

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP du serveur")
        layout.addWidget(self.ip_input)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        layout.addWidget(self.port_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        connect_button = QPushButton("Se connecter")
        connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(connect_button)

        signup_button = QPushButton("Inscription")
        signup_button.clicked.connect(self.sign_up)
        layout.addWidget(signup_button)

        quit_button = QPushButton("Quitter")
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)



    def connect_to_server(self):
        host = self.ip_input.text()
        port = int(self.port_input.text())
        username = self.username_input.text()
        password = self.password_input.text()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_socket.connect((host, port))
            client_socket.send(f"/connect {username} {password}".encode())
            reply = client_socket.recv(1024).decode()

            if reply.strip() == "co":
                connection_details = ConnectionDetails(host, port, username, password, client_socket)
                self.close()
                client_window = ClientWindow(connection_details)
                client_window.show()
            elif reply.strip() == "admin":
                connection_details = ConnectionDetails(host, port, username, password, client_socket)
                self.close()
                admin_window = AdminWindow(connection_details)
                admin_window.show()
            else:
                QMessageBox.warning(self, "Erreur de connexion", "Connexion refusée.")
                client_socket.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la connexion : {e}")

    def sign_up(self):
        host = self.ip_input.text()
        port = int(self.port_input.text())
        username = self.username_input.text()
        password = self.password_input.text()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_socket.connect((host, port))
            client_socket.send(f"/sign-up {username} {password}".encode())
            reply = client_socket.recv(1024).decode()

            if reply.strip() == "co":
                connection_details = ConnectionDetails(host, port, username, password, client_socket)
                self.close()
                client_window = ClientWindow(connection_details)
                client_window.show()
            else:
                QMessageBox.warning(self, "Erreur d'inscription", "Inscription refusée.")
                client_socket.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'inscription : {e}")
class ClientWindow(QMainWindow):
    def __init__(self, connection_details):
        super().__init__()

        self.setWindowTitle("Client2")
        self.connection_details = connection_details
        self.received_messages = QTextEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.received_messages)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        try:
            self.received_messages.append(f"Connecté au serveur sur {self.connection_details.host}:{self.connection_details.port}")

            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

            self.get_room_list()  # Appeler la méthode pour récupérer la liste des salons

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la connexion : {e}")
            self.close()

    def get_room_list(self):
        try:
            self.connection_details.client_socket.send("/liste salon".encode())
            reply = self.connection_details.client_socket.recv(1024).decode()

            rooms = reply.split('|')
            tab_widget = QTabWidget()

            for room in rooms:
                room_details = room.split(';')
                room_name = room_details[0]
                tab_widget.addTab(QWidget(), room_name)

            tab_widget.addTab(QWidget(), "salon_général")
            layout = QVBoxLayout()
            layout.addWidget(tab_widget)
            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

            # Créer et afficher la deuxième fenêtre ici
            client_window = ClientWindow(self.connection_details)
            client_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération de la liste des salons : {e}")

    def receive_messages(self):
        while True:
            try:
                reply = self.connection_details.client_socket.recv(1024).decode()
                if not reply:
                    self.received_messages.append("Le serveur s'est déconnecté")
                    self.quit_app()
                    break
                self.received_messages.append(reply)

            except Exception as e:
                self.received_messages.append(f"Une erreur s'est produite lors de la réception des messages : {e}")
                self.quit_app()
                break

    def send_message(self):
        message = self.input_field.text()
        try:
            self.connection_details.client_socket.send(message.encode())
            self.input_field.clear()

        except Exception as e:
            self.received_messages.append(f"Une erreur s'est produite : {e}")

    def quit_app(self):
        self.connection_details.client_socket.send("bye".encode())
        self.connection_details.client_socket.close()
        QApplication.quit()

    def closeEvent(self, event):
        self.quit_app()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection_window = ConnectionWindow()
    connection_window.show()
    sys.exit(app.exec())
