
import socket
import time
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
host = '127.0.0.1'
port = 12345




class MaFenetre(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client logarithme népérien")
        layout = QVBoxLayout()

        label_fonction = QLabel("fonction:")
        self.text_fonction = QLineEdit()
        layout.addWidget(label_fonction)
        layout.addWidget(self.text_fonction)

        label_min = QLabel("valeur minimale:")
        self.text_min = QLineEdit()
        layout.addWidget(label_min)
        layout.addWidget(self.text_min)

        label_max = QLabel("valeur maximale:")
        self.text_max = QLineEdit()
        layout.addWidget(label_max)
        layout.addWidget(self.text_max)

        label_pas = QLabel("pas:")
        self.text_pas = QLineEdit()
        layout.addWidget(label_pas)
        layout.addWidget(self.text_pas)

        label_resultat = QLabel("resultat:")
        self.text_resultat = QLineEdit()
        self.text_resultat.setReadOnly(True)
        layout.addWidget(label_resultat)
        layout.addWidget(self.text_resultat)

        button_calcul = QPushButton("calcul")
        button_calcul.clicked.connect(self.calculer)
        layout.addWidget(button_calcul)

        button_quitter = QPushButton("quitter")
        button_quitter.clicked.connect(self.fermer)
        layout.addWidget(button_quitter)

        self.setLayout(layout)

    def fermer(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        client_socket.send("arret".encode())
        client_socket.close()
        self.close()
    def calculer(self):

        fonction = self.text_fonction.text()
        val_min = self.text_min.text()
        val_max = self.text_max.text()
        pas = self.text_pas.text()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connecté au serveur sur {host}:{port}")

        client_socket.send(fonction.encode())
        time.sleep(0.1)
        client_socket.send(val_min.encode())
        reply = client_socket.recv(1024).decode()

        self.text_resultat.setText(reply)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MaFenetre()
    fenetre.show()
    sys.exit(app.exec())
