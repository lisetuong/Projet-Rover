import network
import socket
import time

# --- 1. Démarrage du point d'accès ---
ap = network.WLAN(network.AP_IF)
ap.config(ssid='Rover-Lise', password='rover1234')
ap.active(True)

while not ap.active():
    time.sleep(0.1)

print('AP démarré, IP:', ap.ifconfig()[0])  # → 192.168.4.1

# --- 2. Serveur TCP simple ---
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('En attente de connexion...')

conn, client_addr = s.accept()
print('Connecté par', client_addr)

while True:    
    data = conn.recv(1024)
    print('Reçu:', data)
    conn.send(b'OK: ' + data)  # echo
    if data == b"q":
        break


conn.close()