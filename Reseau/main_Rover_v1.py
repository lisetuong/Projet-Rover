from IPSA_Rover_Network_v1 import IpsaRoverNetwork
from IPSA_Rover_Lib import IpsaRoverLib
import Fonctions_ROVER_2 as Rover
import time

net = IpsaRoverNetwork('Rover-Lise', 'rover1234')
net.start()

driver = IpsaRoverLib()

while True:
    # --- Mission autonome ---
    distance = 42   # lecture capteur ultrason par exemple

    # Envoyer des données au PC
    net.send("distance", distance)
    net.send({"cap": 90})   # ou plusieurs à la fois

    # Vérifier les commandes reçues du PC
    msg = net.receive()
    if msg:
        print("Commande reçue :", msg)
        if msg.startswith("move="):
            distance_cm = int(msg.split("=")[1])
            Rover.linear_move_cm(distance_cm)
        
        if msg.startswith("lateral="):
            distance_cm = int(msg.split("=")[1])
            Rover.lateral_move_cm(distance_cm)
        
        if msg.startswith("turn="):
            angle = int(msg.split("=")[1])
            Rover.turn_degree(angle)
        
        if msg.startswith("mission="):
            statut = int(msg.split("=")[1])
            Rover.mission(statut)
            net.send("statut", statut)

    time.sleep(0.1)