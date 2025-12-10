from machine import I2C, Pin
import time
import motor_driver_lib as motor

if __name__ == "__main__":
    # Initialisation I2C + moteur
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=200000)
    motor.init_i2c(i2c)
    motor.set_motor_parameters()

    try:
        # Test des moteurs
        DURATION = 3.0      # secondes
        print(f"Controle moteurs... pendant = {DURATION} s")

        # Avance ligne droite
        motor.control_motor_pwm(-1000, -1000, -1000, -1000)
        time.sleep(DURATION)
        print("Arrêt moteurs.")
        motor.control_motor_pwm(0, 0, 0, 0)

        # Avance droite
        motor.control_motor_pwm(1000, -1000, -1000, 1000)
        time.sleep(DURATION)
        print("Arrêt moteurs.")
        motor.control_motor_pwm(0, 0, 0, 0)

        # Avance diagonale droite
        motor.control_motor_pwm(0, -1000, -1000, 0)
        time.sleep(DURATION)
        print("Arrêt moteurs.")
        motor.control_motor_pwm(0, 0, 0, 0)

        # Tourne droite
        motor.control_motor_pwm(1000, 1000, -1000, -1000)
        time.sleep(DURATION)
        print("Arrêt moteurs.")
        motor.control_motor_pwm(0, 0, 0, 0)

        # Tourne autour droite
        motor.control_motor_pwm(0, 0, -1000, -1000)
        time.sleep(DURATION)
        print("Arrêt moteurs.")
        motor.control_motor_pwm(0, 0, 0, 0)

        # Tourne autour arrière
        motor.control_motor_pwm(1000, 0, -1000, 0)
        time.sleep(DURATION)
        print("Arrêt moteurs.")
        motor.control_motor_pwm(0, 0, 0, 0)

    except KeyboardInterrupt:
        motor.control_motor_pwm(0, 0, 0, 0)
        print("Interruption par clavier. Arrêt moteurs.")
