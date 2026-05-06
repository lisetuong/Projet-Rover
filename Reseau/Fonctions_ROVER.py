import math
import time
from IPSA_Rover_Lib import IpsaRoverLib

driver = IpsaRoverLib()

trajet = [(0, 0)] 
orientation = 90  # On part vers le "haut" (90°) par défaut

start_encoder = None
current_mode = None   # "linear", "lateral", "rotate"
start_orientation = None

def calcul_coo(distance, orientation):
    last_x, last_y = trajet[-1]

    dx = distance * math.cos(math.radians(orientation))
    dy = distance * math.sin(math.radians(orientation))

    x = round(last_x + dx, 3)
    y = round(last_y + dy, 3)

    trajet.append((x, y))
    print(f"📍 Position enregistrée : x={x}, y={y} (Distance parcourue: {distance}cm)")

def linear_move_cm(distance_cm):
    """
    distance_cm > 0 : déplacement en avant
    """
    ticks_target = int(abs(distance_cm) * 124)
    start = driver.read_total_encoder_counts()[0]
    start_time = time.time()

    if distance_cm > 0:
        driver.control_motor_speed(-200, -200, -200, -200)
    else:
        driver.control_motor_speed(200, 200, 200, 200)

    while True:
        current = driver.read_total_encoder_counts()[0]
        if abs(current - start) >= ticks_target:
            break
        time.sleep(0.01)

    driver.control_motors_pwm(0, 0, 0, 0)

    temps_ecoule = time.time() - start_time
    distance_reelle = 12* temps_ecoule

    print(f"Temps : {temps_ecoule:.2f}s | Distance (PWM=200) : {distance_reelle:.2f} cm")

    calcul_coo(distance_reelle if distance_cm > 0 else -distance_reelle, orientation)

def lateral_move_cm(distance_cm):
    """
    distance_cm > 0 : déplacement à droite
    """
    ticks_target = int(abs(distance_cm) * 124)
    start = driver.read_total_encoder_counts()[0]
    start_time = time.time()

    if distance_cm > 0:
        driver.control_motor_speed(200, -200, -200, 200)
        sens = orientation - 90
    else:
        driver.control_motor_speed(-200, 200, 200, -200)
        sens = orientation + 90

    while True:
        current = driver.read_total_encoder_counts()[0]
        if abs(current - start) >= ticks_target:
            break
        time.sleep(0.01)

    driver.control_motors_pwm(0, 0, 0, 0)

    temps_ecoule = time.time() - start_time
    distance_reelle = 12 * temps_ecoule

    print(f"Lateral | Temps : {temps_ecoule:.2f}s | Distance : {distance_reelle:.2f} cm")

    calcul_coo(distance_reelle if distance_cm > 0 else -distance_reelle, sens)

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

def forward():
    global start_encoder, current_mode
    start_encoder = driver.read_total_encoder_counts()[0]
    current_mode = "linear"
    driver.control_motor_speed(-200, -200, -200, -200)

def backward():
    global start_encoder, current_mode
    start_encoder = driver.read_total_encoder_counts()[0]
    current_mode = "linear"
    driver.control_motor_speed(200, 200, 200, 200)

def right():
    global start_encoder, current_mode
    start_encoder = driver.read_total_encoder_counts()[0]
    current_mode = "lateral"
    driver.control_motor_speed(200, -200, -200, 200)

def left():
    global start_encoder, current_mode
    start_encoder = driver.read_total_encoder_counts()[0]
    current_mode = "lateral"
    driver.control_motor_speed(-200, 200, 200, -200)

def turn_left():
    global start_encoder, current_mode, start_orientation
    start_encoder = driver.read_total_encoder_counts()[0]
    start_orientation = orientation
    current_mode = "rotate"
    driver.control_motor_speed(-200, -200, 200, 200)

def turn_right():
    global start_encoder, current_mode, start_orientation
    start_encoder = driver.read_total_encoder_counts()[0]
    start_orientation = orientation
    current_mode = "rotate"
    driver.control_motor_speed(200, 200, -200, -200)

def stop():
    global start_encoder, current_mode, orientation

    driver.control_motors_pwm(0, 0, 0, 0)

    if start_encoder is None:
        return

    end_encoder = driver.read_total_encoder_counts()[0]
    delta_ticks = abs(end_encoder - start_encoder)

    distance_cm = delta_ticks / 124

    if current_mode == "linear":
        calcul_coo(distance_cm, orientation)

    elif current_mode == "lateral":
        sens = orientation - 90
        calcul_coo(distance_cm, sens)

    elif current_mode == "rotate":
        # approx angle
        angle = delta_ticks / 248
        orientation += angle
        orientation %= 360
        print(f"🔄 Nouvelle orientation : {orientation}°")

    start_encoder = None
    current_mode = None

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

def mission(statut):
    try:
        if statut == 0:
            raise KeyboardInterrupt
        
        turn_servo(90)
        driver.control_motors_pwm(0,0,0,0)

        start_encoder = driver.read_total_encoder_counts()[0]
        driver.control_motor_speed(-200, -200, -200, -200)

        while statut == 1:
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