import socket
import tkinter as tk

# --- Connexion au rover ---
s = socket.socket()
s.connect(('192.168.4.1', 8080))
s.setblocking(False)          # ← clé : recv() ne bloque plus

# --- Interface Tkinter ---
win = tk.Tk()
win.title("Contrôle Rover")

label_distance = tk.Label(win, text="distance=?", font=("Arial", 20))
label_distance.pack(pady=10)

def envoyer_vitesse(v):
    try:
        s.send(f"vitesse={v}\n".encode())
    except OSError:
        pass

win.bind("<Up>",   lambda e: envoyer_vitesse(100))
win.bind("<Down>", lambda e: envoyer_vitesse(0))

# --- Boucle de réception non bloquante ---
def lire_rover():
    try:
        data = s.recv(1024).decode()
        for ligne in data.strip().splitlines():
            print("Rover :", ligne)
            if ligne.startswith("distance="):
                label_distance.config(text=ligne)
    except BlockingIOError:
        pass    # pas de données disponibles, c'est normal
    finally:
        win.after(100, lire_rover)   # ← rappel dans 100 ms

win.after(100, lire_rover)
win.mainloop()

s.close()