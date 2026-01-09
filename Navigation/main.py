import time
from IPSA_ROVER_Lib import IpsaRoverLib

driver = IpsaRoverLib()

def avance_cm(distance_cm):
    """
    distance_cm positive = déplacement vers l'avant
    """
    temps = distance_cm / 19.4
    if distance_cm > 0:
        driver.control_motor_speed(-200,-200,-200,-200)
    else:
        driver.control_motor_speed(200,200,200,200)
    time.sleep(temps)
    driver.control_motor_speed(0,0,0,0)

def cote_cm(distance_cm):
    """
    distance_cm positive = déplacement sur la droite
    """
    temps = distance_cm / 19.4
    if distance_cm > 0:
        driver.control_motor_speed(200,-200,-200,200)
    else:
        driver.control_motor_speed(-200,200,200,-200)
    time.sleep(temps)
    driver.control_motor_speed(0,0,0,0)

def tourne_degre(angle):
    driver.control_motor_speed(200,200,-200,-200)
    time.sleep(3)
    driver.control_motor_speed(0,0,0,0)

avance_cm(20)
cote_cm(20)