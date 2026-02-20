import network
import socket
import time
import json

# 🔹 Paramètres WiFi
SSID = "PC_LT"
PASSWORD = "coed-pc-lise"

# 🔹 IP du PC
PC_IP = "10.9.161.15"
PORT = 5005

# Connexion WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(1)

print("Connecté :", wlan.ifconfig())

# Création socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Exemple coordonnées
coo = [(10,10), (20,15), (30,40), (60,30)]

while True:
    print("TEST")
    message = json.dumps(coo)
    sock.sendto(message.encode(), (PC_IP, PORT))
    time.sleep(1)