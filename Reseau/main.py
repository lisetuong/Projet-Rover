import time
from IPSA_Rover_Lib import IpsaRoverLib
from IPSA_Rover_Network_v1 import IpsaRoverNetwork
import Fonctions_ROVER as ROVER

driver = IpsaRoverLib()
net = IpsaRoverNetwork("RoverLTV","RoverLTV")

if __name__ == "__main__":
    net.start()