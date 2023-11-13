import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.resize(250, 0)
        self.setWindowTitle("Test Timothée")
        self.setWindowIcon(QIcon('C:/Users/e2200466/PycharmProjects/R3.09/int_graph/icon.png'))

        layout = QVBoxLayout()

        label = QLabel("Saisir votre nom:")
        self.name_input = QLineEdit()
        ok = QPushButton("Ok")
        quit = QPushButton("Quitter")
        self.result_label = QLabel()

        ok.clicked.connect(self.action_ok)
        quit.clicked.connect(self.action_quitter)

        layout.addWidget(label)
        layout.addWidget(self.name_input)
        layout.addWidget(ok)
        layout.addWidget(self.result_label)
        layout.addWidget(quit)
        self.setLayout(layout)

    def action_ok(self):
        entered_name = self.name_input.text()
        self.result_label.setText(f"Bonjour, {entered_name}!")

    def action_quitter(self):
        QCoreApplication.instance().quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    root = MyWidget()
    root.show()
    sys.exit(app.exec())
