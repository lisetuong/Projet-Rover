import math
import time
import network
import socket
import json
from IPSA_Rover_Lib import IpsaRoverLib

driver = IpsaRoverLib()

SSID = "PC_CV"
PASSWORD = "codechloepc"
PC_IP = "10.36.87.144"
PORT = 5005

trajet = [(0, 0)] 
orientation = 90  # On part vers le "haut" (90°) par défaut

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def setup_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Tentative de connexion WiFi...")
    
    # Attendre 10 secondes max pour la connexion
    retry = 0
    while not wlan.isconnected() and retry < 20:
        time.sleep(0.5)
        retry += 1
    
    if wlan.isconnected():
        print("Connecté ! IP du Rover :", wlan.ifconfig()[0])
    else:
        print("Échec de connexion WiFi. Vérifie le partage de connexion.")

def calcul_coo(distance, orientation):
    last_x, last_y = trajet[-1]

    dx = distance * math.cos(math.radians(orientation))
    dy = distance * math.sin(math.radians(orientation))

    x = round(last_x + dx, 3)
    y = round(last_y + dy, 3)

    trajet.append((x, y))
    print(f"📍 Position enregistrée : x={x}, y={y} (Distance parcourue: {distance}cm)")
    
    #envoi au PC : 
    try:
        message = json.dumps(trajet)
        sock.sendto(message.encode(), (PC_IP, PORT))
    except:
        pass


def turn_degree(angle):
    """
    angle > 0 : tourne à gauche
    angle < 0 : tourne à droite
    """
    global orientation
    # Calcul physique du mouvement (ne pas trop toucher si ça marche)
    arc_cm = abs(angle) * 3.1416 * 17.1 / 360
    ticks_target = int(arc_cm * 248)
    start = driver.read_total_encoder_counts()[0]

    if angle < 0: # Droite
        driver.control_motor_speed(200, 200, -200, -200)
    else: # Gauche
        driver.control_motor_speed(-200, -200, 200, 200)

    while abs(driver.read_total_encoder_counts()[0] - start) < ticks_target:
        time.sleep(0.01)

    driver.control_motors_pwm(0, 0, 0, 0)
    
    # Mise à jour de la boussole interne
    orientation += angle
    orientation %= 360
    print(f"🔄 Nouvelle orientation : {orientation}°")


def turn_servo(angle):
    pulse_us = int(800 + angle * (1800 / 180))
    driver.set_servo_pulse_us(pulse_us)
    time.sleep(0.5)

def sonar_distance():
    temps = driver.read_sonar_echo_time_ms()
    if temps is not None:
        distance_cm = (temps * 0.001 * 340 / 2) * 100
        return distance_cm
    return 1000

def eviter_obstacle():
    print("Obstacle détecté. Analyse du terrain...")
    driver.control_motors_pwm(0, 0, 0, 0) # Stop immédiat

    # Regarder à Droite (0°)
    turn_servo(0)
    dist_droite = sonar_distance()
    time.sleep(0.3)

    # Regarder à Gauche (180°)
    turn_servo(180)
    dist_gauche = sonar_distance()
    time.sleep(0.3)
    
    # Replacer le servo au centre (90°)
    turn_servo(90)
    
    # Cas 1 : Coincé des deux côtés (inférieur à 10 cm)
    if dist_droite < 10 and dist_gauche < 10:
        print("Coincé ! Demi-tour complet.")
        turn_degree(180) # Fait un demi-tour
        
    # Cas 2 : Plus d'espace à droite
    elif dist_droite > dist_gauche:
        print(f"Espace à droite ({dist_droite}cm). Rotation à droite.")
        turn_degree(-90) 
        
    # Cas 3 : Plus d'espace à gauche (ou égalité)
    else:
        print(f"Espace à gauche ({dist_gauche}cm). Rotation à gauche.")
        turn_degree(90)

def mission():
    try:
        setup_wifi()
        turn_servo(90)
        driver.control_motors_pwm(0,0,0,0)

        start_encoder = driver.read_total_encoder_counts()[0]
        driver.control_motor_speed(-200, -200, -200, -200)

        while True:
            dist = sonar_distance()
            if dist < 15:
                driver.control_motors_pwm(0, 0, 0, 0)
                
                current_encoder = driver.read_total_encoder_counts()[0]
                distance_cm = abs(current_encoder - start_encoder) / 124
                
                # Cette fonction va maintenant envoyer l'info en WiFi toute seule !
                calcul_coo(distance_cm, orientation)
                
                eviter_obstacle()
                
                start_encoder = driver.read_total_encoder_counts()[0]
                driver.control_motor_speed(-200, -200, -200, -200)

            time.sleep(0.1)
    
    except KeyboardInterrupt:
        driver.control_motors_pwm(0, 0, 0, 0)
        print("Fin du parcours.")