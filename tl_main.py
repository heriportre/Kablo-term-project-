import math
import numpy as np
from scipy.stats import gmean


mu0 = 4*math.pi*1e-7
eps0 = 8.85*1e-12

# Conductor types and their specifications
conductor_specs = {
    "Hawk": {"diameter": 21.793, "GMR": 8.809, "R": 0.132},
    "Drake": {"diameter": 28.143, "GMR": 11.369, "R": 0.080},
    "Cardinal": {"diameter": 30.378, "GMR": 12.253, "R": 0.067},
    "Rail": {"diameter": 29.591, "GMR": 11.765, "R": 0.068},
    "Pheasant": {"diameter": 35.103, "GMR": 14.204, "R": 0.051}
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
            R = conductor_spec["R"] * self.length 
            
            
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
                #bs is vector list [bc, bc', b'c, b'c']
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
                arr_req_oneph = [math.sqrt(math.exp(-0.25)*int(1e-3*conductor_spec["diameter"])/2*(self.coordinates[i]-self.coordinates[-i])) for i in range(3)] #for R_eq
                req2 = gmean(arr_req_oneph) #r_eq for 2 ct
            
            else:
                raise(ValueError,"unexpected error occurred while calculating GMR or R_eq")
            
            arr.append(1e-3*int(conductor_spec["GMR"])) # add the gmr_conductor into array wihch is arr=[d d..] 
            GMR = gmean(arr) if (self.num_circuits == 1)  else gmr_2
            
            arr_r.append(1e-3*math.exp(-0.25)*int(conductor_spec["diameter"])/2)
            R_eq = gmean(arr_r) if (self.num_circuits == 1)  else req2
        

            ### Calculate L AND R 
        
            L = 2e-7 * math.log(GMD / GMR)  # Henries per meter
            L *= self.length * 1000  # Convert to mH
            
            # Calculate line charging capacitance C (µF)
            C = 2 * math.pi * 8.85419e-12 / math.log(GMD / R_eq)  # Farads per meter
            C *= self.length * 1000000  # Convert to uF
            
            ### CALCULATE INDUCTANCE L AND C ACCORDING TO TL MODEL (MEDIUM LENGTH,LONG LENGTH ETC.) ???###
            #L=
            #C=

            # Calculate line capacity (MVA)
            if self.num_circuits == 1:
                voltage = tower_spec["voltage"]
            else:
                voltage = tower_spec["voltage"] * math.sqrt(2)
            capacity = self.num_conductors * voltage * math.sqrt(3) / 1000

            return { #DEBUG USING THIS SECTION
                "R (Ω)": R, #round(R, 3)
                "L (mH)": L, #round(L, 3)
                "C (µF)": C, #round(C * 1e6, 3)
                "Capacity (MVA)": round(capacity, 3)
            }
        except KeyError:
            return "Invalid tower type"
        except ValueError as e:
            return str(e)

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

# Main function
def main():
    tower_type, num_circuits, coordinates, num_conductors, conductor_type, distance_between_conductors, length = get_user_input()
    line = TransmissionLine(tower_type, num_circuits, coordinates, num_conductors, conductor_type, distance_between_conductors, length)
    result = line.calculate_parameters()
    print(result)

if __name__ == "__main__":
    main()

