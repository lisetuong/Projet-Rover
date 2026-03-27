import socket
import json
import matplotlib.pyplot as plt

PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

# On prépare la fenêtre de dessin
plt.ion() # Mode interactif pour mettre à jour le dessin
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-o', label="Trajet du Rover")
ax.set_xlabel("X (cm)")
ax.set_ylabel("Y (cm)")
ax.set_title("Cartographie en temps réel")
ax.grid(True)

print("En attente de données...")

while True:
    try:
        data, addr = sock.recvfrom(4096)
        message = data.decode()
        trajet = json.loads(message) # On reçoit la liste de points [(0,0), (10,0)...]
        
        # On extrait les X et les Y pour le dessin
        x_vals = [p[0] for p in trajet]
        y_vals = [p[1] for p in trajet]
        
        # On met à jour le graphique
        line.set_data(x_vals, y_vals)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(0.1)
        
        print("Position mise à jour :", trajet[-1])
    except Exception as e:
        print("Erreur :", e)