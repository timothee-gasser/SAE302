import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QPushButton, QWidget, QMessageBox, QGridLayout
from PyQt6.QtGui import QIcon
class TemperatureConverter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Convertisseur de Température")
        self.setWindowIcon(QIcon('icon.png'))

        layout = QGridLayout()


        label_temp = QLabel("Température:")
        self.input_temp = QLineEdit()
        layout.addWidget(label_temp, 0, 0)
        layout.addWidget(self.input_temp, 0, 1)

        self.temp_label = QLabel("")
        layout.addWidget(self.temp_label, 0, 2)


        self.convert_button = QPushButton("Convertir")
        self.convert_button.clicked.connect(self.convert_temperature)
        layout.addWidget(self.convert_button, 1, 1)

        self.convert_direction_combo = QComboBox()
        self.convert_direction_combo.addItems(["°C à K", "K à °C"])
        self.convert_direction_combo.currentIndexChanged.connect(self.update_temp_labels)
        layout.addWidget(self.convert_direction_combo, 1, 2)


        label_conversion = QLabel("Conversion:")
        self.result_conversion = QLineEdit()
        self.result_conversion.setReadOnly(True)
        layout.addWidget(label_conversion, 2, 0)
        layout.addWidget(self.result_conversion, 2, 1)

        self.result_unit_label = QLabel("")
        layout.addWidget(self.result_unit_label, 2, 2)

        self.help_button = QPushButton("?")
        self.help_button.clicked.connect(self.show_help_message)
        layout.addWidget(self.help_button, 3, 3)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def convert_temperature(self):
        try:
            temperature = float(self.input_temp.text())
            if self.convert_direction_combo.currentText() == "°C à K":
                if temperature < -273.15:
                    raise ValueError("La température en Celsius ne peut pas être inférieure à -273.15°C (zéro absolu)")
                converted_temp = temperature + 273.15
                converted_unit = "K"
            else:
                if temperature < 0:
                    raise ValueError("La température en Kelvin ne peut pas être inférieure à 0°K")
                converted_temp = temperature - 273.15
                converted_unit = "°C"

            self.result_conversion.setText(f"{converted_temp:.2f}")
            self.result_unit_label.setText(converted_unit)
        except ValueError as e:
            QMessageBox.critical(self, "Erreur", str(e))
            self.result_conversion.clear()
            self.result_unit_label.clear()

    def update_temp_labels(self):

        direction = self.convert_direction_combo.currentText()
        if direction == "°C à K":
            self.temp_label.setText("°C")
            self.result_unit_label.setText("K")
        else:
            self.temp_label.setText("K")
            self.result_unit_label.setText("°C")

    def show_help_message(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Aide")
        msg_box.setText("Permet de convertir un nombre soit de Kelvin vers Celcus, soit de Celcus vers Kelvin")
        ok_button = msg_box.addButton(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        if msg_box.clickedButton() == ok_button:
            msg_box.close()

def main():
    app = QApplication(sys.argv)
    converter = TemperatureConverter()
    converter.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
