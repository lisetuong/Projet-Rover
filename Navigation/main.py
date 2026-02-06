import time
from IPSA_ROVER_Lib import IpsaRoverLib

driver = IpsaRoverLib()

def linear_move_cm(distance_cm):
    """
    distance_cm > 0 : déplacement en avant
    """
    ticks_target = int(distance_cm * 124)

    start_ticks = driver.read_total_encoder_counts()
    start = start_ticks[0]  # on prend un moteur de référence

    driver.control_motor_speed(-200, -200, -200, -200)

    while True:
        current = driver.read_total_encoder_counts()[0]
        if abs(current - start) >= ticks_target:
            break
        time.sleep(0.01)

    driver.control_motors_pwm(0, 0, 0, 0)

def lateral_move_cm(distance_cm):
    """
    distance_cm > 0 : déplacement à droite
    """
    ticks_target = int(distance_cm * 124)
    start = driver.read_total_encoder_counts()[0]

    driver.control_motor_speed(200, -200, -200, 200)

    while True:
        current = driver.read_total_encoder_counts()[0]
        if abs(current - start) >= ticks_target:
            break
        time.sleep(0.01)

    driver.control_motors_pwm(0, 0, 0, 0)

def turn_degree(angle):
    """
    angle > 0 : tourne à droite
    angle < 0 : tourne à gauche
    """
    arc_cm = abs(angle) * 3.1416 * 17.1 / 360
    ticks_target = int(arc_cm * 248)

    start = driver.read_total_encoder_counts()[0]

    if angle > 0:
        driver.control_motor_speed(200, 200, -200, -200)
    else:
        driver.control_motor_speed(-200, -200, 200, 200)

    while True:
        current = driver.read_total_encoder_counts()[0]
        if abs(current - start) >= ticks_target:
            break
        time.sleep(0.01)

    driver.control_motors_pwm(0, 0, 0, 0)

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

turn_servo(0)
turn_servo(90)
turn_servo(180)
linear_move_cm(20)
lateral_move_cm(20)
turn_degree(90)
while True:
    sonar_distance()