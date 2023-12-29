import threading
import sys
import socket
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QMessageBox, QTabWidget
from PyQt6.QtGui import QColor
import time

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
        self.received_messages = QTextEdit()
        self.received_messages.setReadOnly(True)

        layout = QVBoxLayout()
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
        self.connection_details.client_socket.send("/bye".encode())
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

    def display_client_window(self, connection_details):
        self.client_window = ClientWindow(connection_details)
        self.client_window.show()

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
                self.display_client_window(connection_details)
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
                self.display_client_window(connection_details)
            else:
                QMessageBox.warning(self, "Erreur d'inscription", "Inscription refusée.")
                client_socket.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'inscription : {e}")
class SalonThread(threading.Thread):
    def __init__(self, client_socket, room_name, received_messages_widget, tab_index):
        super().__init__()
        self.client_socket = client_socket
        self.room_name = room_name
        self.received_messages = received_messages_widget
        self.tab_index = tab_index
        self.running = True

    def run(self):
        while self.running:
            try:
                reply = self.client_socket.recv(1024)
                if not reply:
                    self.received_messages.append("Le serveur s'est déconnecté")
                    break
                reply = reply.decode()
                self.display_message(reply)
            except Exception as e:
                self.received_messages.append(f"Erreur : {e}")
                break

    def stop(self):
        self.running = False

    def display_message(self, message):
        print(message)
        messages = message.split('\n')
        for msg in messages:
            if msg.startswith(f":{self.room_name}"):
                _, msg_content = msg.split(" ", 1)
                self.received_messages.append(msg_content)


class ClientWindow(QMainWindow):
    def __init__(self, connection_details):
        super().__init__()

        self.setWindowTitle("Client2")
        self.connection_details = connection_details
        self.rooms_messages = {}

        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        self.setup_general_tab()
        layout.addWidget(self.tab_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        try:
            self.get_room_list()
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la connexion : {e}")
            self.close()

    def setup_general_tab(self):
        general_layout = QVBoxLayout()
        general_received_messages = QTextEdit()
        general_received_messages.setReadOnly(True)
        general_layout.addWidget(general_received_messages)

        general_input_field = QLineEdit()
        general_layout.addWidget(general_input_field)

        general_send_button = QPushButton("Envoyer")
        general_send_button.clicked.connect(lambda _, msg=general_input_field: self.send_general_message(msg))
        general_layout.addWidget(general_send_button)

        self.tab_widget.addTab(QWidget(), "général")
        self.tab_widget.widget(self.tab_widget.count() - 1).setLayout(general_layout)
        self.rooms_messages["général"] = general_received_messages

    def receive_messages(self):
        while self.running:
            try:
                reply = self.connection_details.client_socket.recv(1024).decode()
                if not reply:
                    self.rooms_messages["général"].append("Le serveur s'est déconnecté")
                    self.quit_app()
                    break

                self.process_received_message(reply)
            except Exception as e:
                self.quit_app()
                break

            time.sleep(0.1)

    def process_received_message(self, message):
        print(message)
        if message.startswith(":"):
            prefix, msg = message.split(" ", 1)
            room_name = prefix[1:]
            if room_name in self.rooms_messages:
                self.rooms_messages[room_name].append(msg)
                print(self.rooms_messages)
        else:
            self.rooms_messages["général"].append(message)

    def get_room_list(self):
        try:
            self.connection_details.client_socket.send("/liste salon".encode())
            reply = self.connection_details.client_socket.recv(1024).decode()

            rooms = reply.split('|')
            tab_widget = QTabWidget()

            general_layout = QVBoxLayout()
            general_received_messages = QTextEdit()
            general_received_messages.setReadOnly(True)
            general_layout.addWidget(general_received_messages)

            general_input_field = QLineEdit()
            general_layout.addWidget(general_input_field)

            general_send_button = QPushButton("Envoyer")
            general_send_button.clicked.connect(lambda _, msg=general_input_field: self.send_general_message(msg))
            general_layout.addWidget(general_send_button)

            tab_widget.addTab(QWidget(), "général")
            tab_widget.widget(tab_widget.count() - 1).setLayout(general_layout)

            salon_threads = []

            for room in rooms:
                room_details = room.split(';')
                room_name = room_details[0]

                tab_layout = QVBoxLayout()
                received_messages = QTextEdit()
                received_messages.setReadOnly(True)
                tab_layout.addWidget(received_messages)

                input_field = QLineEdit()
                tab_layout.addWidget(input_field)

                send_button = QPushButton("Envoyer")
                send_button.clicked.connect(lambda _, msg=input_field, rm=room_name: self.send_message(msg, rm))
                tab_layout.addWidget(send_button)

                tab_widget.addTab(QWidget(), room_name)
                tab_widget.widget(tab_widget.count() - 1).setLayout(tab_layout)

                salon_thread = SalonThread(
                    self.connection_details.client_socket,
                    room_name,
                    received_messages,
                    tab_widget.count() - 1
                )
                salon_thread.start()
                salon_threads.append(salon_thread)

            layout = QVBoxLayout()
            layout.addWidget(tab_widget)
            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

            for i in range(min(tab_widget.count(), len(rooms))):
                tab_data = rooms[i].split(';')
                if tab_data[2] == "False":
                    tab_widget.tabBar().setTabTextColor(i, QColor("red"))

            # Retourner les threads créés pour une gestion ultérieure
            return salon_threads

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération de la liste des salons : {e}")

    def receive_messages(self):
        while True:
            try:
                reply = self.connection_details.client_socket.recv(1024).decode()
                if not reply:
                    self.rooms_messages["général"].append("Le serveur s'est déconnecté")
                    self.quit_app()
                    break
            except Exception as e:
                self.quit_app()
                break

    def send_message(self, input_field, room_name):
        message = input_field.text()
        try:
            self.connection_details.client_socket.send(f"/salon {room_name} {message}".encode())
            input_field.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite : {e}")

    def send_general_message(self, input_field):
        message = input_field.text()
        try:
            self.connection_details.client_socket.send(f"{message}".encode())
            input_field.clear()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors de l'envoi du message : {e}")

    def quit_app(self):
        self.connection_details.client_socket.send("/bye".encode())
        self.connection_details.client_socket.close()
        QApplication.quit()

    def closeEvent(self, event):
        salon_threads = self.get_room_list()
        for thread in salon_threads:
            thread.stop()
        self.quit_app()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection_window = ConnectionWindow()
    connection_window.show()
    sys.exit(app.exec())



