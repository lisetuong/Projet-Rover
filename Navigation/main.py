import math
import time
from IPSA_ROVER_Lib import IpsaRoverLib
import Fonctions_ROVER as ROVER

driver = IpsaRoverLib()

if __name__ == "__main__":
    try:
        ROVER.turn_servo(90) # Regarder devant
        while True:
            dist = ROVER.sonar_distance()
            
            if dist < 10:
                ROVER.eviter_obstacle()
            else:
                # Avancer doucement tant que la voie est libre
                # On utilise control_motor_speed en continu sans boucle while interne
                driver.control_motor_speed(-200, -200, -200, -200)
            
            time.sleep(0.05) 

    except KeyboardInterrupt:
        driver.control_motors_pwm(0, 0, 0, 0)