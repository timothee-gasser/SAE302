import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox

class ConversionTemperatureApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Conversion de Température")


        self.temperature_label = QLabel("Température:")
        self.temperature_entry = QLineEdit()
        self.unit_label_input = QLabel()

        self.convert_button = QPushButton("Convertir")
        self.convert_button.clicked.connect(self.convert_temperature)
        self.conversion_type_combobox = QComboBox()
        self.conversion_type_combobox.addItems(["°C vers °K", "°K vers °C"])


        self.result_label = QLabel("Conversion:")
        self.result_entry = QLineEdit()
        self.result_entry.setReadOnly(True)
        self.unit_label_output = QLabel()

        # Quatrième ligne (mise à jour de l'unité en fonction de la conversion)
        self.unit_combobox_input = QComboBox()
        self.update_unit_combobox()

        # Layout
        layout = QVBoxLayout()


        input_layout = QHBoxLayout()
        input_layout.addWidget(self.temperature_label)
        input_layout.addWidget(self.temperature_entry)
        input_layout.addWidget(self.unit_label_input)  # Ajout du QLabel à la mise en page
        layout.addLayout(input_layout)


        convert_layout = QHBoxLayout()
        convert_layout.addWidget(self.convert_button)
        convert_layout.addWidget(self.conversion_type_combobox)
        layout.addLayout(convert_layout)

        result_layout = QHBoxLayout()
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.result_entry)
        result_layout.addWidget(self.unit_label_output)
        layout.addLayout(result_layout)



        self.update_unit_combobox()

        self.setLayout(layout)

    def convert_temperature(self):
        try:
            temperature = float(self.temperature_entry.text())
        except ValueError:
            self.show_error("Veuillez saisir une valeur numérique.")
            return

        conversion_type = self.conversion_type_combobox.currentText()

        # Mise à jour de l'unité d'entrée
        if "°C" in conversion_type:
            self.unit_label_input.setText("°C")
        elif "°K" in conversion_type:
            self.unit_label_input.setText("°K")

        if conversion_type == "°C vers °K":
            if temperature < -273.15:
                self.show_error("La température est inférieure au zéro absolu.")
            else:
                converted_temperature = temperature + 273.15
                self.result_entry.setText(str(converted_temperature))
                self.unit_label_output.setText("°K")

        elif conversion_type == "°K vers °C":
            if temperature < 0:
                self.show_error("La température est inférieure au zéro absolu.")
            else:
                converted_temperature = temperature - 273.15
                self.result_entry.setText(str(converted_temperature))
                self.unit_label_output.setText("°C")

    def update_unit_combobox(self):
        conversion_type = self.conversion_type_combobox.currentText()

        if "°C" in conversion_type:
            self.unit_combobox_input.clear()
            self.unit_label_input.setText("°C")  # Mettez à jour l'unité d'entrée
        elif "°K" in conversion_type:
            self.unit_combobox_input.clear()
            self.unit_label_input.setText("°K")  # Mettez à jour l'unité d'entrée

    def show_error(self, message):
        QMessageBox.critical(self, "Erreur", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConversionTemperatureApp()
    window.show()
    sys.exit(app.exec_())
