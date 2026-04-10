from IPSA_Rover_Network_v1 import IpsaRoverNetwork
import time

net = IpsaRoverNetwork('Rover-Lise', 'rover1234')
net.start()

vitesse = 50

while True:
    # --- Mission autonome ---
    distance = 42   # lecture capteur ultrason par exemple

    # Envoyer des données au PC
    net.send("distance", distance)
    net.send({"vitesse": vitesse, "cap": 90})   # ou plusieurs à la fois

    # Vérifier les commandes reçues du PC
    msg = net.receive()
    if msg:
        print("Commande reçue :", msg)
        if msg.startswith("vitesse="):
            vitesse = int(msg.split("=")[1])

    time.sleep(0.1)