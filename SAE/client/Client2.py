import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QMessageBox,QHBoxLayout, QTabWidget,QLabel, QListWidget,QListWidgetItem
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal

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
class MessageReceiverThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.running = True

    def run(self):
        while self.running:
            try:
                reply = self.client_socket.recv(1024).decode()
                if not reply:
                    self.message_received.emit("Le serveur s'est déconnecté")
                    break
                self.message_received.emit(reply)
            except Exception as e:
                self.message_received.emit(f"Erreur : {e}")
                break

    def stop(self):
        self.running = False

class ClientWindow(QMainWindow):
    def __init__(self, connection_details):
        super().__init__()
        self.running = True
        self.setWindowTitle("Client2")
        self.connection_details = connection_details
        self.message_receiver_thread = None
        self.current_room_name = None
        self.tab_widgets = []
        self.create_menu_bar()

        central_layout = QHBoxLayout()  # Utiliser un QHBoxLayout pour organiser les widgets horizontalement

        # Liste des utilisateurs
        users_layout = QVBoxLayout()
        self.users_widget = QListWidget()
        users_layout.addWidget(self.users_widget)
        central_layout.addLayout(users_layout)  # Ajouter la liste des utilisateurs à la disposition centrale

        # Onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.change_current_room)
        central_layout.addWidget(self.tab_widget)  # Ajouter les onglets à la disposition centrale

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.get_room_list()
        self.tab_widget.currentChanged.connect(self.reset_tab_color)
        self.get_user_list()

    def get_user_list(self):
        try:
            self.connection_details.client_socket.send("/liste util".encode())
            reply = self.connection_details.client_socket.recv(1024).decode()

            users = reply.split('|')
            for user_info in users:
                user_name, user_state = user_info.split(';')
                item = QListWidgetItem(f"{user_name} - {user_state}")
                self.users_widget.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération de la liste des utilisateurs : {e}")
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        demande_menu = menu_bar.addMenu('Demande')

        salon_action = QAction('Salon', self)
        salon_action.triggered.connect(self.open_join_salon_request)
        demande_menu.addAction(salon_action)

        ticket_action = QAction('Ticket', self)
        ticket_action.triggered.connect(self.open_ticket_request)
        demande_menu.addAction(ticket_action)
    def open_join_salon_request(self):
        self.join_salon_window = JoinSalonRequestWindow(self.connection_details)
        self.join_salon_window.show()
    def open_ticket_request(self):
        self.join_ticket_window = JoinTicketRequestWindow(self.connection_details)
        self.join_ticket_window.show()
    def get_room_list(self):
        try:
            self.connection_details.client_socket.send("/liste salon".encode())
            reply = self.connection_details.client_socket.recv(1024).decode()

            rooms = reply.split('|')

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

                quit_button = QPushButton("Quitter")
                quit_button.clicked.connect(self.quit_app)
                tab_layout.addWidget(quit_button)

                self.tab_widget.addTab(QWidget(), room_name)
                self.tab_widget.widget(self.tab_widget.count() - 1).setLayout(tab_layout)

            for i in range(min(self.tab_widget.count(), len(rooms))):
                tab_data = rooms[i].split(';')
                if tab_data[2] == "False":
                    label = QLabel("Vous ne faites pas partie de ce salon. Envoyez une demande pour y accéder.")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)


                    self.tab_widget.setTabText(i, tab_data[0])
                    self.tab_widget.widget(i).layout().addWidget(label)

                    self.tab_widget.tabBar().setTabTextColor(i, QColor("red"))


            self.start_message_receiver()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la récupération de la liste des salons : {e}")
    def reset_tab_color(self, index):
        if index >= 0:
            self.tab_widget.tabBar().setTabTextColor(index, QColor("black"))
    def start_message_receiver(self):
        self.message_receiver_thread = MessageReceiverThread(self.connection_details.client_socket)
        self.message_receiver_thread.message_received.connect(self.filter_and_display_messages)
        self.message_receiver_thread.start()
    def filter_and_display_messages(self, message):
        room_indicators = [f":{tab_name}" for tab_name in self.get_room_names()]
        for indicator in room_indicators:
            if message.startswith(indicator):
                _, msg_content = message.split(" ", 1)
                room_name = indicator[1:]
                index = self.get_room_index(room_name)
                if index >= 0:
                    received_messages_widget = self.tab_widget.widget(index).layout().itemAt(0).widget()
                    received_messages_widget.append(msg_content)
                    if index != self.tab_widget.currentIndex():
                        self.tab_widget.tabBar().setTabTextColor(index, QColor("blue"))
    def get_room_names(self):
        return [self.tab_widget.tabText(i) for i in range(self.tab_widget.count())]
    def get_room_index(self, room_name):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == room_name:
                return i
        return -1
    def change_current_room(self, index):
        if index >= 0:
            self.current_room_name = self.tab_widget.tabText(index)
            self.tab_widget.tabBar().setTabTextColor(index, QColor("black"))
    def send_message(self, input_field, room_name):
        message = input_field.text()
        try:
            self.connection_details.client_socket.send(f"/salon {room_name} {message}".encode())
            input_field.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite : {e}")
    def change_current_room(self, index):
        if index >= 0:
            self.current_room_name = self.tab_widget.tabText(index)
    def quit_app(self):
        self.connection_details.client_socket.send("/bye".encode())
        if self.message_receiver_thread:
            self.message_receiver_thread.stop()
            self.message_receiver_thread.wait()

        self.connection_details.client_socket.close()
        QApplication.quit()
    def closeEvent(self, event):
        self.quit_app()
class JoinSalonRequestWindow(QMainWindow):
    def __init__(self, connection_details):
        super().__init__()
        self.connection_details = connection_details
        self.setWindowTitle("Demande pour rejoindre un salon")

        layout = QVBoxLayout()

        label = QLabel("Demande pour rejoindre un salon")
        layout.addWidget(label)

        self.salon_name_input = QLineEdit()
        self.salon_name_input.setPlaceholderText("Nom du salon")
        layout.addWidget(self.salon_name_input)

        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Raison")
        layout.addWidget(self.reason_input)

        send_button = QPushButton("Envoyer")
        send_button.clicked.connect(self.send_salon_request)
        layout.addWidget(send_button)

        quit_button = QPushButton("Quitter")
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def send_salon_request(self):
        salon_name = self.salon_name_input.text()
        reason = self.reason_input.text()
        request_message = f"/demande_salon {salon_name} {reason}"
        self.connection_details.client_socket.send(request_message.encode())
        self.close()
class JoinTicketRequestWindow(QMainWindow):
    def __init__(self, connection_details):
        super().__init__()
        self.connection_details = connection_details
        self.setWindowTitle("Demande pour création de ticket")

        layout = QVBoxLayout()

        label = QLabel("Création de Ticket")
        layout.addWidget(label)

        self.type_ticket_input = QLineEdit()
        self.type_ticket_input.setPlaceholderText("tupe de demande")
        layout.addWidget(self.type_ticket_input)

        self.demande_input = QLineEdit()
        self.demande_input.setPlaceholderText("Demande")
        layout.addWidget(self.reason_input)

        send_button = QPushButton("Envoyer")
        send_button.clicked.connect(self.send_ticket_request)
        layout.addWidget(send_button)

        quit_button = QPushButton("Quitter")
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def send_ticket_request(self):
        type_ticket = self.type_ticket_input.text()
        demande = self.demande_input.text()
        request_message = f"/demande {type_ticket} {demande}"
        self.connection_details.client_socket.send(request_message.encode())
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection_window = ConnectionWindow()
    connection_window.show()
    sys.exit(app.exec())