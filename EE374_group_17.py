import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QComboBox,
    QSpinBox, QDoubleSpinBox, QLineEdit, QPushButton, QLabel, QGridLayout, QGroupBox,QMessageBox
)
from PySide6.QtCore import Qt
import math
import numpy as np
from scipy.stats import (gmean)


mu0 = 4*math.pi*1e-7
eps0 = 8.85*1e-12

# Conductor types and their specifications
conductor_specs = {
    "Hawk": {"diameter": 21.793, "GMR": 8.809, "R": 0.132, "I": 659},
    "Drake": {"diameter": 28.143, "GMR": 11.369, "R": 0.080, "I": 907},
    "Cardinal": {"diameter": 30.378, "GMR": 12.253, "R": 0.067, "I": 996},
    "Rail": {"diameter": 29.591, "GMR": 11.765, "R": 0.068, "I": 993},
    "Pheasant": {"diameter": 35.103, "GMR": 14.204, "R": 0.051, "I": 1187}
}

# Tower types and their specifications
tower_types = {
    "Type-1": {"max_height": 39, "min_height": 23, "max_horizontal": 4, "min_horizontal": 2.2, "voltage": 66000, "max_bundle": 3},
    "Type-2": {"max_height": 43, "min_height": 38.25, "max_horizontal_side": 11.5, "min_horizontal_side": 9.4, "max_horizontal_center": 8.9, "voltage": 400000, "max_bundle": 4},
    "Type-3": {"max_height": 48.8, "min_height": 36, "max_horizontal": 5.35, "min_horizontal": 1.8, "voltage": 154000, "max_bundle": 3}
}

class TransmissionLine:
    def __init__(self, tower_type, num_circuits, coordinates, num_conductors, conductor_type, distance_between_conductors, length):
        self.tower_type = tower_type
        self.num_circuits = num_circuits
        self.coordinates = coordinates
        self.num_conductors = num_conductors
        self.conductor_type = conductor_type
        self.distance_between_conductors = distance_between_conductors
        self.length = length

    def calculate_parameters(self):
        try:
            # Check if tower type is valid
            tower_spec = tower_types[self.tower_type]
            #### ToDO: X-Y COORDINATE RESTRICTIONS OF CORRESPONDING TOWERS IS GOING TO BE DONE ###
            
            
            # Check if number of circuits is valid
            if self.num_circuits not in [1, 2]:
                raise ValueError("Invalid number of circuits")            
            
            # Check if number of conductors is valid
            if self.num_conductors > tower_spec["max_bundle"]:
                raise ValueError(f"Number of conductors exceeds maximum for {self.tower_type} tower")

            # Check if conductor type is valid
            if self.conductor_type not in conductor_specs:
                raise ValueError("Invalid conductor type")

            conductor_spec = conductor_specs[self.conductor_type]

            # Calculate line resistance R (Ω)
            R = conductor_spec["R"] * self.length / self.num_conductors
            
            
            #calc GMD
            arr_gmd =[]
            if self.num_circuits == 1: 
                arr_gmd.append(np.linalg.norm(np.subtract(self.coordinates[0],self.coordinates[1])))
                arr_gmd.append(np.linalg.norm(np.subtract(self.coordinates[0],self.coordinates[2])))
                arr_gmd.append(np.linalg.norm(np.subtract(self.coordinates[1],self.coordinates[2]))) #distance between phase b and c 
                GMD = gmean(arr_gmd)
            elif self.num_circuits == 2:
                ab = [np.subtract(self.coordinates[0],self.coordinates[1]),np.subtract(self.coordinates[0],self.coordinates[2]),np.subtract(self.coordinates[-1],self.coordinates[1]),np.subtract(self.coordinates[-1],self.coordinates[-2])]
                ac = [np.subtract(self.coordinates[0],self.coordinates[2]),np.subtract(self.coordinates[0],self.coordinates[3]),np.subtract(self.coordinates[-1],self.coordinates[2]),np.subtract(self.coordinates[-1],self.coordinates[3])]
                bc = [np.subtract(self.coordinates[1],self.coordinates[2]),np.subtract(self.coordinates[1],self.coordinates[3]),np.subtract(self.coordinates[-2],self.coordinates[2]),np.subtract(self.coordinates[-2],self.coordinates[3])]
                #bc is vector list [bc, bc', b'c, b'c']
                for i in range(4):
                    ab = [np.linalg.norm(ab[i])]
                    ac = [np.linalg.norm(ac[i])]
                    bc = [np.linalg.norm(bc[i])] #iterate over vector list and calculate magnitude of the vectors in list bc
                    
                ab_=gmean(ab) 
                ac_=gmean(ac)
                bc_=gmean(bc) #gmd of phase b and c
                GMD = gmean([ab_,ac_,bc_]) #gmd between phases
            
            else:
                raise(ValueError,"unexpected error occurred while calculating GMD")
            

                
            
            
            #GMR and R_eq calculation
            arr = []
            arr_r = []
            if self.num_circuits==1:
                if self.num_conductors < 4:
                    arr = [self.distance_between_conductors for i in range(int(self.num_conductors)-1)] #add d into array n-1 times(n= # of conductors in a bundle)
                    arr_r = arr #array for r_eq
                elif self.num_conductors ==4: 
                    arr = [self.distance_between_conductors for i in range(int(self.num_conductors)-2)] #add d into array n-2 times
                    arr.append(self.distance_between_conductors*math.sqrt(2)) # add dkök2 into array if 4 cond in a bundle
                    arr_r = arr
            elif self.num_circuits ==2: # 2 ct 6 fazlı t.line 
                arr_gmr_of_each_ph = [math.sqrt(1e-3*int(conductor_spec["GMR"])*np.linalg.norm((self.coordinates[i]-self.coordinates[-i-1]))) for i in range(3)]#list formed by gmr's of each phase i.e. arr_gmr_of_each_ph =[gmr_aa', gmr_bb', gmr_cc'] where gmr_aa'= sqrt(gmr_cond*dis_aa')
                gmr_2 = gmean(arr_gmr_of_each_ph) # gmr of list: arr_gmr_of_each_ph =[gmr_aa', gmr_bb', gmr_cc'] (for 2 ct)
                arr_req_oneph = [math.sqrt(int(1e-3*conductor_spec["diameter"])/2*(self.coordinates[i]-self.coordinates[-i])) for i in range(3)] #for R_eq
                req2 = gmean(arr_req_oneph) #r_eq for 2 ct
            
            else:
                raise(ValueError,"unexpected error occurred while calculating GMR or R_eq")
            
            arr.append(1e-3*int(conductor_spec["GMR"])) # add the gmr_conductor into array wihch is arr=[d d..] 
            GMR = gmean(arr) if (self.num_circuits == 1)  else gmr_2
            
            arr_r.append(1e-3*int(conductor_spec["diameter"])/2)
            R_eq = gmean(arr_r) if (self.num_circuits == 1)  else req2
        

            ### Calculate L AND R 
        
            L = 2e-7 * math.log(GMD / GMR)  # Henries per meter
            L *= self.length * 1000  # Convert to mH
            
            # Calculate line charging capacitance C (µF)
            C = (2 * math.pi * 8.85419e-12) / (math.log(GMD / R_eq))  # Farads per meter
            C *= self.length * 1000000  # Convert to uF
            
            ### CALCULATE INDUCTANCE L AND C ACCORDING TO TL MODEL (MEDIUM LENGTH,LONG LENGTH ETC.) ???###
            #L=
            #C=

            # Calculate line capacity (MVA)
            voltage = tower_spec["voltage"] if (self.num_circuits == 1)  else 2*tower_spec["voltage"]
                            
            current = conductor_spec["I"]*self.num_conductors
            capacity = current * voltage * math.sqrt(3) / 1000

            return { #DEBUG USING THIS SECTION
                "R (Ω)": R*1000, 
                "L (mH)": L*1000, 
                "C (µF)": C*1000, 
                "Capacity (MVA)": capacity
            }
        except KeyError:
            return "Invalid tower type"
        except ValueError as e:
            return str(e)
        











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
        self.tower_type.addItems(list(tower_types.keys()))
        self.form_layout.addRow("Tower Type:", self.tower_type)

        # Number of circuits
        self.num_circuits = QSpinBox()
        self.num_circuits.setRange(1, 2)
        self.form_layout.addRow("Number of Circuits:", self.num_circuits)

        # X-Y coordinates of phase lines as input, for example each circuit has 3 phases. Each phase has X and Y coordinates.
        self.coord_layout = QGridLayout()
        self.phase_coords = {}
        for i in range(2):  
            for j in range(3):  
                coord = QLineEdit()                
                self.phase_coords[f"Phase {j+1} Circuit {i+1} x, y"] = coord
                self.coord_layout.addWidget(QLabel(f"Phase {j+1} Circuit {i+1}:"), i, 2*j)
                self.coord_layout.addWidget(coord, i, 2*j+1)


        self.form_layout.addRow("Phase Line Coordinates Set Input as x, y:", self.coord_layout)

        # Number of conductors in the bundle
        self.num_conductors = QSpinBox()
        self.num_conductors.setRange(1, 4)  # Example range
        self.form_layout.addRow("Number of Conductors in Bundle:", self.num_conductors)

        # Distance between conductors in the bundle
        self.bundle_distance = QDoubleSpinBox()
        self.bundle_distance.setRange(0.1, 10.0)  # Example range
        self.bundle_distance.setSingleStep(0.1)
        self.form_layout.addRow("Distance Between Conductors in Bundle (m):", self.bundle_distance)

        # Conductor type
        self.conductor_type = QComboBox()
        self.conductor_type.addItems(list(conductor_specs.keys()))
        self.form_layout.addRow("Conductor Type:", self.conductor_type)

        # Length of the transmission line
        self.transmission_length = QDoubleSpinBox()
        self.transmission_length.setRange(0.1, 100000.0)  # Example range
        self.transmission_length.setSingleStep(0.1)
        self.form_layout.addRow("Length of Transmission Line (km):", self.transmission_length)

        self.layout.addLayout(self.form_layout)

    def create_buttons(self):
        self.parameter_input_label = QLabel("")
        self.layout.addWidget(self.parameter_input_label, alignment=Qt.AlignCenter)

        self.calculate_button = QPushButton("Calculate")
        # make a large button with large font
        self.calculate_button.setStyleSheet("font-size: 28px;")
        self.calculate_button.clicked.connect(self.calculate_parameters)
        self.layout.addWidget(self.calculate_button, alignment=Qt.AlignCenter)

        self.result_label = QLabel("")
        self.layout.addWidget(self.result_label, alignment=Qt.AlignCenter)

    def calculate_parameters(self):
        # Extract values from inputs
        tower_type = self.tower_type.currentText()
        num_circuits = self.num_circuits.value()
        phase_coords = {key: value.text() for key, value in self.phase_coords.items()}
        # convert phase coordinates to two dimensional list
        try:
            if num_circuits == 1:
                # remove the second circuit's coordinates
                phase_coords = {key: value for key, value in phase_coords.items() if "Circuit 1" in key}
                phase_coords = [[float(coord) for coord in value.split(",")] for value in phase_coords.values()]
                if tower_type=="Type-1" and (not (23 < phase_coords[0][1] < 39)) and (not (23 < phase_coords[1][1] < 39)) and (not (23 < phase_coords[2][1] < 39)):
                    raise ValueError("y coordinates of tower must be in range between 23m and 39m")
                if tower_type=="Type-1" and (not (2.2 < abs(phase_coords[0][0]) < 4)) and (not (2.2 < abs(phase_coords[1][0]) < 4)) and (not (2.2 < abs(phase_coords[2][0]) < 4)):
                    raise ValueError("x  coordinates of tower must far away at most 4m and at least 2.2m ")    

                if tower_type=="Type-2" and (not (38.25 < phase_coords[0][1] < 43)) and (not (38.25 < phase_coords[1][1] < 43)) and (not (38.25 < phase_coords[2][1] < 43)):
                    raise ValueError("y coordinates of tower must be in range between 38.25m and 43m")
                if tower_type=="Type-2" and (not (9.4 < abs(phase_coords[0][0]) < 11.5)) and (not (9.4 < abs(phase_coords[2][0]) < 11.5)):
                    raise ValueError("x coordinates of side phases must far away at most 11.5m and at least 9.4m ") 
                if tower_type=="Type-2" and (not (-8.9 < phase_coords[1][0] < 8.9)):
                    raise ValueError("x coordinates of center phase must far away at most 8.9m")


            elif num_circuits == 2:
                phase_coords = [[float(coord) for coord in value.split(",")] for value in phase_coords.values()]
                if tower_type=="Type-3" and (not (36 < phase_coords[:][1] < 48.8)):
                    raise ValueError("y coordinates of tower must be in range between 36m and 48.8m")
                if tower_type=="Type-3" and (not (1.8 < abs(phase_coords[:][0]) < 5.35)):
                    raise ValueError("x coordinates of side phases must far away at most 1.8m and at least 5.35m ") 

            num_conductors = self.num_conductors.value()
            bundle_distance = self.bundle_distance.value()
            conductor_type = self.conductor_type.currentText()
            transmission_length = self.transmission_length.value()



        except ValueError as e:
            print("Error caught in calculate_parameters:", e)  # Print the caught error
            self.show_error(str(e))  # Show the error in a QMessageBox
            return  # Exit the function if an error is caught

        # Placeholder for actual calculation logic
        # In a real application, perform the necessary calculations here
        result = f"Calculating with:\nTower Type: {tower_type}\nNumber of Circuits: {num_circuits}\n"
        result += f"Phase Coordinates: {phase_coords}\nNumber of Conductors: {num_conductors}\n"
        result += f"Bundle Distance: {bundle_distance} m\nConductor Type: {conductor_type}\n"
        result += f"Transmission Length: {transmission_length} km"

        self.parameter_input_label.setText(result)

        line = TransmissionLine(tower_type, num_circuits, phase_coords, num_conductors, conductor_type, bundle_distance, transmission_length)
        result = line.calculate_parameters()
        # if result is a dictionary then display the results as a table
        if isinstance(result, dict):
            result_str = ""
            for key, value in result.items():
                result_str += f"{key}: {value}\n"
            # make it bold and bigger
            self.result_label.setStyleSheet("font-weight: bold; font-size: 16px;")
            self.result_label.setText(result_str)
        elif isinstance(result, str):
            QMessageBox.critical(self, "Error", result)
        else:    
            self.result_label.setText(str(result))
            
    def show_error(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransmissionLineCalculator()
    window.show()
    sys.exit(app.exec())



# Function to get user input
def get_user_input():

    tower_type = input("Enter tower type (Type-1, Type-2, Type-3): ")
    num_circuits = int(input("Enter number of circuits (1 or 2): "))
    coordinates = []
    for i in range(num_circuits):
        for j in range(3):
            print(f"For phase {j+1} in Circuit {i+1}:")
            x = float(input(f"Enter X coordinate of the phase {j+1} in meters: "))
            y = float(input(f"Enter Y coordinate of the phase {j+1 } in meters: "))
            coordinates.append([x, y])
        
        
    num_conductors = int(input("Enter number of conductors in the bundle: "))
    conductor_type = input("Enter conductor type (Hawk, Drake, Cardinal, Rail, Pheasant): ")
    distance_between_conductors = float(input("Enter distance between conductors inside the bundle (in meters): "))
    length = float(input("Enter length of the transmission line (in kilometers): "))

    
    return tower_type, num_circuits, coordinates, num_conductors, conductor_type, distance_between_conductors, length
