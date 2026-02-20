import math
import time
#import matplotlib.pyplot as plt
from IPSA_ROVER_Lib import IpsaRoverLib

driver = IpsaRoverLib()

coo = [(0,0)]
orientation = 0

VITESSE_PWM_200_CM_S = 12.0
last_update_time = None

def calcul_coo(distance, orientation):
    dx = distance * math.cos(math.radians(orientation))
    dy = distance * math.sin(math.radians(orientation))

    x = round(coo[-1][0] + dx, 3)
    y = round(coo[-1][1] + dy, 3)

    coo.append((x,y))
    print(f"Position actuelle : {coo[-1]}")

"""
def dessin_trajet():
    x_vals = [p[0] for p in coo]
    y_vals = [p[1] for p in coo]

    plt.figure()
    plt.plot(x_vals, y_vals, 'b', marker='o')
    plt.axhline(0, color='black')
    plt.axvline(0, color='black')

    plt.xlabel("X (cm)")
    plt.ylabel("Y (cm)")
    plt.title("Trajet du Rover")
    plt.gca().set_aspect('equal', adjustable='box')

    x_last, y_last = coo[-1]

    dx = 0.1 * math.cos(math.radians(orientation))
    dy = 0.1 * math.sin(math.radians(orientation))

    plt.arrow(x_last, y_last, dx, dy, head_width=1, color="r")

    plt.show()
"""

def distance_par_pwm_200(temps_s):
    return VITESSE_PWM_200_CM_S * temps_s

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
    distance_reelle = distance_par_pwm_200(temps_ecoule)

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
    distance_reelle = distance_par_pwm_200(temps_ecoule)

    print(f"Lateral | Temps : {temps_ecoule:.2f}s | Distance : {distance_reelle:.2f} cm")

    calcul_coo(distance_reelle if distance_cm > 0 else -distance_reelle, sens)

def turn_degree(angle):
    """
    angle > 0 : tourne à gauche
    angle < 0 : tourne à droite
    """
    arc_cm = abs(angle) * 3.1416 * 17.1 / 360
    ticks_target = int(arc_cm * 248)

    start = driver.read_total_encoder_counts()[0]

    if angle < 0:
        driver.control_motor_speed(200, 200, -200, -200)
    else:
        driver.control_motor_speed(-200, -200, 200, 200)

    while True:
        current = driver.read_total_encoder_counts()[0]
        if abs(current - start) >= ticks_target:
            break
        time.sleep(0.01)

    driver.control_motors_pwm(0, 0, 0, 0)

    global orientation
    orientation += angle
    orientation %= 360

def turn_servo(angle):
    """
    angle = 0° = droite = 800us
    angle = 90° = milieu = 1750us
    angle = 180° = gauche = 2600us
    """
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180

    pulse_us = int(800 + angle * (1800 / 180))
    driver.set_servo_pulse_us(pulse_us)
    time.sleep(0.5)

def sonar_distance():
    temps = driver.read_sonar_echo_time_ms()
    if temps != None:
        temps *= 0.001
        distance_m = (temps * 340) / 2
        distance_cm = distance_m * 100
        print(f"{distance_cm} cm")
        return distance_cm
    return 10000

def eviter_obstacle():
    print("Obstacle détecté. Analyse du terrain...")
    driver.control_motors_pwm(0, 0, 0, 0) # Stop immédiat

    # Regarder à Droite (0°)
    turn_servo(0)
    dist_droite = sonar_distance()
    
    # Regarder à Gauche (180°)
    turn_servo(180)
    dist_gauche = sonar_distance()
    
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