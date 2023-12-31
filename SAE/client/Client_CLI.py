import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QMessageBox
"""
Client CLI
"""
class ConnectionDetails:
    def __init__(self, host, port, username, password, client_socket):
        """
        Représente les détails de la connexion pour un utilisateur.

        Args:
            host (str): L'adresse de l'hôte.
            port (int): Le port de connexion.
            username (str): Le nom d'utilisateur.
            password (str): Le mot de passe de l'utilisateur.
            client_socket (socket): Le socket client associé à l'utilisateur.

        Attributes:
            host (str): L'adresse de l'hôte.
            port (int): Le port de connexion.
            username (str): Le nom d'utilisateur.
            password (str): Le mot de passe de l'utilisateur.
            client_socket (socket): Le socket client associé à l'utilisateur.

        Notes:
            Cette classe stocke les détails de connexion d'un utilisateur, notamment l'adresse de l'hôte,
            le port de connexion, le nom d'utilisateur, le mot de passe et le socket client associé à cet utilisateur.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_socket = client_socket
class AdminWindow(QMainWindow):
    def __init__(self, connection_details):
        """
        Fenêtre administrateur de l'interface en ligne de commande.

        Args:
            connection_details (ConnectionDetails): Détails de connexion pour l'utilisateur.

        Attributes:
            received_messages (QTextEdit): Champ texte pour afficher les messages reçus.
            input_field (QLineEdit): Champ pour entrer les messages à envoyer.
            connection_details (ConnectionDetails): Détails de connexion pour l'utilisateur.

        Notes:
            Cette classe représente la fenêtre administrateur de l'interface en ligne de commande.
            Elle permet à l'administrateur de se connecter au serveur et d'envoyer/recevoir des messages.
        """
        super().__init__()

        self.setWindowTitle("Fenêtre Admin CLI")
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
            self.received_messages.append("Si vous avez besoin d'aide vous pouvez utiliser /? , /help , /admin ?, /admin help")

            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la connexion : {e}")
            self.close()
    def receive_messages(self):
        """
                Reçoit les messages du serveur et les affiche dans la fenêtre.

                Notes:
                    Cette méthode est chargée de recevoir les messages du serveur via la connexion du client.
                    Elle affiche les messages reçus dans la fenêtre de l'interface utilisateur.
                    En cas d'erreur lors de la réception des messages, elle arrête l'écoute et affiche le problème.
        """
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
        """
            Envoie un message saisi par l'utilisateur.

            Notes:
                Cette méthode envoie le message entré par l'utilisateur à travers le socket.
                Elle efface ensuite le champ de saisie.
                En cas d'erreur lors de l'envoi du message, elle affiche un message d'erreur dans la fenêtre.
        """

        message = self.input_field.text()
        try:
            self.connection_details.client_socket.send(message.encode())
            self.input_field.clear()

        except Exception as e:
            self.received_messages.append(f"Une erreur s'est produite : {e}")
    def quit_app(self):
        """
            Termine l'application de l'interface administrateur.

            Notes:
                Cette méthode arrête le thread de réception des messages, envoie un signal de déconnexion au serveur,
                ferme le socket client et quitte l'application QApplication.
        """

        self.receive_thread.stop()
        self.connection_details.client_socket.send("/bye".encode())
        self.connection_details.client_socket.close()
        QApplication.quit()
    def closeEvent(self, event):
        self.quit_app()
class ConnectionWindow(QMainWindow):
    def __init__(self):
        """
                Initialise une fenêtre de connexion au serveur pour le CLI.

                La fenêtre contient des champs pour saisir l'IP du serveur, le port, le nom d'utilisateur et le mot de passe.
                Elle permet de se connecter au serveur ou de s'inscrire en tant qu'utilisateur.
        """
        super().__init__()

        self.setWindowTitle("Connexion au serveur en CLI")

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
        """
                Tente de se connecter au serveur en utilisant les informations saisies.

                Récupère l'IP, le port, le nom d'utilisateur et le mot de passe saisis par l'utilisateur.
                Établit une connexion avec le serveur via un socket.
                Envoie les informations d'identification au serveur et attend la réponse.
                Si la connexion est établie en tant qu'utilisateur standard ('co'), ouvre la fenêtre de client CLI.
                Si la connexion est établie en tant qu'administrateur ('admin'), ouvre la fenêtre d'administration CLI.
                Sinon, affiche un avertissement de connexion refusée.
                En cas d'erreur, affiche une boîte de dialogue avec le détail de l'erreur.
        """
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
        """
                Tente de s'inscrire en utilisant les informations saisies.

                Récupère l'IP, le port, le nom d'utilisateur et le mot de passe saisis par l'utilisateur.
                Établit une connexion avec le serveur via un socket.
                Envoie les informations d'inscription au serveur et attend la réponse.
                Si l'inscription est réussie ('co'), ouvre la fenêtre de client.
                Sinon, affiche un avertissement d'inscription refusée.
                En cas d'erreur, affiche une boîte de dialogue avec le détail de l'erreur.
        """
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
        """
                Initialise la fenêtre du client CLI.

                Affiche une fenêtre pour envoyer et recevoir des messages depuis le serveur.
                Initialise les détails de connexion et lance le thread pour recevoir des messages.

                Args:
                    connection_details (ConnectionDetails): Détails de la connexion au serveur.
                """
        super().__init__()

        self.setWindowTitle("Client CLI")
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
            self.received_messages.append("Si vous avez besoin d'aide vous pouvez utiliser /? , /help")
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la connexion : {e}")
            self.close()
    def receive_messages(self):
        """
                Écoute en permanence les messages du serveur.
                Affiche les messages reçus dans la zone de texte de la fenêtre.
                Arrête l'écoute si une erreur survient ou si le serveur se déconnecte.
        """
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
        """
            Envoie un message au serveur.

            Récupère le texte saisi par l'utilisateur dans la zone de saisie.
            Envoie ce message au serveur via la connexion établie.
            Efface le champ de saisie après l'envoi du message.
            Affiche une erreur si l'envoi du message échoue.
        """
        message = self.input_field.text()
        try:
            self.connection_details.client_socket.send(message.encode())
            self.input_field.clear()

        except Exception as e:
            self.received_messages.append(f"Une erreur s'est produite : {e}")
    def quit_app(self):
        """
            Arrête le thread d'écoute des messages, envoie un signal de déconnexion au serveur,
            puis ferme la connexion au serveur. Enfin, quitte l'application.
        """
        self.receive_thread.stop()
        self.connection_details.client_socket.send("/bye".encode())
        self.connection_details.client_socket.close()
        QApplication.quit()
    def closeEvent(self, event):
        self.quit_app()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection_window = ConnectionWindow()
    connection_window.show()
    sys.exit(app.exec())
