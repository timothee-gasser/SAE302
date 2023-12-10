import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton

class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client")

        layout = QVBoxLayout()

        self.received_messages = QTextEdit()
        self.received_messages.setReadOnly(True)
        layout.addWidget(self.received_messages)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        send_button = QPushButton("Envoyer")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.host = '127.0.0.1'
        self.port = 12345
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((self.host, self.port))
            self.received_messages.append(f"Connecté au serveur sur {self.host}:{self.port}")

            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

        except Exception as e:
            self.received_messages.append(f"Erreur lors de la connexion au serveur : {e}")

    def receive_messages(self):
        while True:
            try:
                reply = self.client_socket.recv(1024).decode()
                if not reply:
                    self.received_messages.append("Le serveur s'est déconnecté")
                    break
                self.received_messages.append(reply)

            except Exception as e:
                self.received_messages.append(f"Une erreur s'est produite lors de la réception des messages : {e}")
                break

    def send_message(self):
        message = self.input_field.text()
        try:
            self.client_socket.send(message.encode())

            if message.lower() == 'bye':
                self.received_messages.append("Le serveur s'est déconnecté")
                self.client_socket.close()

            if message.lower() == 'arret':
                self.received_messages.append("Arrêt du serveur demandé")
                self.client_socket.close()
                sys.exit()

        except Exception as e:
            self.received_messages.append(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_window = ClientWindow()
    client_window.show()
    sys.exit(app.exec())
