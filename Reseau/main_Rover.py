import time
from IPSA_Rover_Lib import IpsaRoverLib
from IPSA_Rover_Network import IpsaRoverNetwork
import Fonctions_Rover as Rover

net = IpsaRoverNetwork('Rover-Lise', 'rover1234')
net.start()
driver = IpsaRoverLib()

def send_position():
    x, y = Rover.trajet[-1]
    net.send({
        "X": x,
        "Y": y,
        "Orientation": Rover.orientation
    })

while True:
    # --- Mission autonome ---
    distance = 42   # lecture capteur ultrason par exemple

    # Envoyer des données au PC
    send_position()

    # Vérifier les commandes reçues du PC
    msg = net.receive()
    if msg:
        for ligne in msg.splitlines():
            print("Commande reçue :", ligne)

            if ligne == "forward":
                Rover.forward()
            elif ligne == "backward":
                Rover.backward()
            elif ligne == "left":
                Rover.left()
            elif ligne == "right":
                Rover.right()
            elif ligne == "turn_left":
                Rover.turn_left()
            elif ligne == "turn_right":
                Rover.turn_right()
            elif ligne == "stop":
                Rover.stop()
        
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
                            send_position()
                            
                            Rover.eviter_obstacle()
                            send_position()
                            
                            start_encoder = driver.read_total_encoder_counts()[0]
                            driver.control_motor_speed(-200, -200, -200, -200)

                        msg = net.receive()
                        if msg and msg.startswith("mission="):
                            statut = int(msg.split("=")[1])

                        time.sleep(0.1)
                
                except KeyboardInterrupt:
                    driver.control_motors_pwm(0, 0, 0, 0)

                    current_encoder = driver.read_total_encoder_counts()[0]
                    distance_cm = abs(current_encoder - start_encoder) / 124
                    if distance_cm > 0:
                        Rover.calcul_coo(distance_cm, Rover.orientation)

                    send_position()
                    print("Fin du parcours.")

    time.sleep(0.1)