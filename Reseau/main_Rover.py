import time
from IPSA_Rover_Lib import IpsaRoverLib
from IPSA_Rover_Network import IpsaRoverNetwork
import Fonctions_ROVER as Rover

net = IpsaRoverNetwork('Rover-Lise', 'rover1234')
net.start()

driver = IpsaRoverLib()

while True:
    # --- Mission autonome ---
    distance = 42   # lecture capteur ultrason par exemple

    # Envoyer des données au PC
    net.send("Orientation", Rover.orientation)
    net.send("Coordonnées", Rover.trajet)   # ou plusieurs à la fois

    # Vérifier les commandes reçues du PC
    msg = net.receive()
    if msg:
        for ligne in msg.splitlines():
            print("Commande reçue :", ligne)

            if ligne == "forward":
                driver.control_motor_speed(-200, -200, -200, -200)
            elif ligne == "backward":
                driver.control_motor_speed(200, 200, 200, 200)
            elif ligne == "left":
                driver.control_motor_speed(-200, 200, 200, -200)
            elif ligne == "right":
                driver.control_motor_speed(200, -200, -200, 200)
            elif ligne == "turn_left":
                driver.control_motor_speed(-200, -200, 200, 200)
            elif ligne == "turn_right":
                driver.control_motor_speed(200, 200, -200, -200)
            elif ligne == "stop":
                driver.control_motors_pwm(0, 0, 0, 0)
        
            if ligne.startswith("move="):
                distance_cm = int(ligne.split("=")[1])
                Rover.linear_move_cm(distance_cm)
            
            if ligne.startswith("lateral="):
                distance_cm = int(ligne.split("=")[1])
                Rover.lateral_move_cm(distance_cm)
            
            if ligne.startswith("turn="):
                angle = int(ligne.split("=")[1])
                Rover.turn_degree(angle)
            
            if ligne.startswith("mission="):
                statut = int(ligne.split("=")[1])
                try:
                    if statut == 0:
                        raise KeyboardInterrupt
                    
                    Rover.turn_servo(90)
                    driver.control_motors_pwm(0,0,0,0)

                    start_encoder = driver.read_total_encoder_counts()[0]
                    driver.control_motor_speed(-200, -200, -200, -200)

                    while statut == 1:
                        dist = Rover.sonar_distance()
                        if dist < 15:
                            driver.control_motors_pwm(0, 0, 0, 0)
                            
                            current_encoder = driver.read_total_encoder_counts()[0]
                            distance_cm = abs(current_encoder - start_encoder) / 124
                            
                            # Cette fonction va maintenant envoyer l'info en WiFi toute seule !
                            Rover.calcul_coo(distance_cm, Rover.orientation)
                            
                            Rover.eviter_obstacle()
                            
                            start_encoder = driver.read_total_encoder_counts()[0]
                            driver.control_motor_speed(-200, -200, -200, -200)

                        msg = net.receive()
                        if msg and msg.startswith("mission="):
                            statut = int(msg.split("=")[1])

                        time.sleep(0.1)
                
                except KeyboardInterrupt:
                    driver.control_motors_pwm(0, 0, 0, 0)
                    print("Fin du parcours.")

    time.sleep(0.1)