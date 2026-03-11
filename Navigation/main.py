import time
from IPSA_ROVER_Lib import IpsaRoverLib
import Fonctions_ROVER as ROVER

driver = IpsaRoverLib()

if __name__ == "__main__":
    try:
        # 1. On connecte le WiFi avant de partir !
        ROVER.setup_wifi()
        
        ROVER.turn_servo(90)
        start_encoder = driver.read_total_encoder_counts()[0]
        driver.control_motor_speed(-200, -200, -200, -200)

        while True:
            dist = ROVER.sonar_distance()
            if dist < 15:
                driver.control_motors_pwm(0, 0, 0, 0)
                
                current_encoder = driver.read_total_encoder_counts()[0]
                distance_cm = abs(current_encoder - start_encoder) / 124
                
                # Cette fonction va maintenant envoyer l'info en WiFi toute seule !
                ROVER.calcul_coo(distance_cm, ROVER.orientation)
                
                ROVER.eviter_obstacle()
                
                start_encoder = driver.read_total_encoder_counts()[0]
                driver.control_motor_speed(-200, -200, -200, -200)

            time.sleep(0.1)

    except KeyboardInterrupt:
        driver.control_motors_pwm(0, 0, 0, 0)
        print("Fin du parcours.")