from machine import I2C, Pin
import time
import motor_driver_lib as motor
import os


# ==============================
# Fonctions utilitaires de LOGGING dans le microcontrôleur Pico W
# ==============================
LOG_DIR = "logs" # Répertoire pour mettre le de log
LOG_FILE = LOG_DIR + "/speed_log0.csv" # Chemin d’accès vers le fichier log
def init_logging():
    """Créer le dossier et le fichier CSV si besoin."""
    if LOG_DIR not in os.listdir():
        os.mkdir(LOG_DIR)
    with open(LOG_FILE, "w") as f:
        f.write("time_ms, V1_rpm, V2_rpm, V3_rpm, V4_rpm\n")
def append_log(temps, V1, V2, V3, V4):
    """Ajoute une ligne dans le fichier CSV."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{temps}, {V1}, {V2}, {V3}, {V4}\n")

# -------------------------
# Contrôle en vitesse d’une seule roue
# -------------------------
# --- Paramètres du PI (à ajuster selon ton identification) ---
Kp = 0.034 # [V/rpm]
Ki = 0.32 # [V/(rpm·s)]
DT = 0.020 # [s] Période d’Echantillonnage (20 ms)
V_MAX = 7.34 # V
def control_vitesse(consigne_V1, duree=5.0):
    """
    consigne_V1 : consigne de vitesse en rpm de la roue 1
    duree : durée du test (s)
    """
    print(f"Control active: Consigne = {consigne_V1} rpm, Duree = {duree}s")
    t_start = time.ticks_ms() # instant de départ
    init_logging()
    while (time.ticks_diff(time.ticks_ms(), t_start) / 1000.0) < duree:
        # Lire l’incrément d’encodeur sur 20 ms
        deltas = motor.read_encoder_deltas()
        V1 = motor.calculate_rpm(deltas[0])
        V2 = motor.calculate_rpm(deltas[1])
        V3 = motor.calculate_rpm(deltas[2])
        V4 = motor.calculate_rpm(deltas[3])
        # Calcul de l’erreur
        error = consigne_V1 - V1
        # Calcul de la tension de commande (PI)
        u = Kp * error
        # Saturation à -7.34 à 7.34 V
        if u > V_MAX:
            u = V_MAX
        elif u < -V_MAX:
            u = -V_MAX
        # Appliquer la tension sur le moteur choisi
        voltages = [u , u, u, u]
        motor.control_motor_voltage(*voltages)
        print(f"Consigne: {consigne_V1:.1f} rpm, Measure: {V1:.2f} rpm, u={u:.2f} V")
        append_log(time.ticks_diff(time.ticks_ms(), t_start),V1,V2,V3,V4)
        time.sleep(DT)
    motor.control_motor_pwm(0, 0, 0, 0)


if __name__ == "__main__":
    # Initialisation I2C + moteur
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=200000)
    motor.init_i2c(i2c)
    motor.set_motor_parameters()

    try:
        """
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
        """
        # Commande de vitesse
        control_vitesse(250)

    except KeyboardInterrupt:
        motor.control_motor_pwm(0, 0, 0, 0)
        print("Interruption par clavier. Arrêt moteurs.")
