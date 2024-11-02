import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QComboBox,
    QSpinBox, QDoubleSpinBox, QLineEdit, QPushButton, QLabel, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt

class TransmissionLineCalculator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Transmission Line Calculator")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)

        self.create_inputs()
        self.create_buttons()

    def create_inputs(self):
        self.form_layout = QFormLayout()

        # Tower type
        self.tower_type = QComboBox()
        self.tower_type.addItems(["Type A", "Type B", "Type C"])
        self.form_layout.addRow("Tower Type:", self.tower_type)

        # Number of circuits
        self.num_circuits = QSpinBox()
        self.num_circuits.setRange(1, 2)
        self.form_layout.addRow("Number of Circuits:", self.num_circuits)

        # X-Y coordinates of phase lines
        self.coord_layout = QGridLayout()
        self.phase_coords = {}
        for i in range(3):
            for j in range(2):
                coord_input = QLineEdit()
                self.coord_layout.addWidget(QLabel(f"Phase {i+1} Circuit {j+1}:"), i, 2*j)
                self.coord_layout.addWidget(coord_input, i, 2*j + 1)
                self.phase_coords[(i, j)] = coord_input

        self.form_layout.addRow("Phase Line Coordinates:", self.coord_layout)

        # Number of conductors in the bundle
        self.num_conductors = QSpinBox()
        self.num_conductors.setRange(1, 8)  # Example range
        self.form_layout.addRow("Number of Conductors in Bundle:", self.num_conductors)

        # Distance between conductors in the bundle
        self.bundle_distance = QDoubleSpinBox()
        self.bundle_distance.setRange(0.1, 10.0)  # Example range
        self.bundle_distance.setSingleStep(0.1)
        self.form_layout.addRow("Distance Between Conductors in Bundle (m):", self.bundle_distance)

        # Conductor type
        self.conductor_type = QComboBox()
        self.conductor_type.addItems(["Type 1", "Type 2", "Type 3", "Type 4", "Type 5"])
        self.form_layout.addRow("Conductor Type:", self.conductor_type)

        # Length of the transmission line
        self.transmission_length = QDoubleSpinBox()
        self.transmission_length.setRange(0.1, 1000.0)  # Example range
        self.transmission_length.setSingleStep(0.1)
        self.form_layout.addRow("Length of Transmission Line (km):", self.transmission_length)

        self.layout.addLayout(self.form_layout)

    def create_buttons(self):
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_parameters)
        self.layout.addWidget(self.calculate_button, alignment=Qt.AlignCenter)

        self.result_label = QLabel("")
        self.layout.addWidget(self.result_label, alignment=Qt.AlignCenter)

    def calculate_parameters(self):
        # Extract values from inputs
        tower_type = self.tower_type.currentText()
        num_circuits = self.num_circuits.value()
        phase_coords = {key: value.text() for key, value in self.phase_coords.items()}
        num_conductors = self.num_conductors.value()
        bundle_distance = self.bundle_distance.value()
        conductor_type = self.conductor_type.currentText()
        transmission_length = self.transmission_length.value()

        # Placeholder for actual calculation logic
        # In a real application, perform the necessary calculations here
        result = f"Calculating with:\nTower Type: {tower_type}\nNumber of Circuits: {num_circuits}\n"
        result += f"Phase Coordinates: {phase_coords}\nNumber of Conductors: {num_conductors}\n"
        result += f"Bundle Distance: {bundle_distance} m\nConductor Type: {conductor_type}\n"
        result += f"Transmission Length: {transmission_length} km"

        self.result_label.setText(result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransmissionLineCalculator()
    window.show()
    sys.exit(app.exec())
