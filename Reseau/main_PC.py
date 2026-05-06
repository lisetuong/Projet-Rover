import socket
import tkinter as tk

# --- Connexion au rover ---
s = socket.socket()
s.connect(('192.168.4.1', 8080))
s.setblocking(False)          # ← clé : recv() ne bloque plus

# --- Interface Tkinter ---
win = tk.Tk()
win.title("Contrôle Rover")

label_distance = tk.Label(win, text="Orientation=?", font=("Arial", 20))
label_distance.pack(pady=10)

def move(distance_cm):
    try:
        s.send(f"move={distance_cm}\n".encode())
    except OSError:
        pass

def lateral(distance_cm):
    try:
        s.send(f"lateral={distance_cm}\n".encode())
    except OSError:
        pass

def turn(distance_cm):
    try:
        s.send(f"turn={distance_cm}\n".encode())
    except OSError:
        pass

def mission(statut):
    try:
        s.send(f"mission={statut}\n".encode())
    except OSError:
        pass

def keypressed(e):
    key = e.keysym
    if key == "Up":
        move(10)
    if key == "Down":
        move(-10)
    if key == "Right":
        lateral(10)
    if key == "Left":
        lateral(-10)
    if key == "b":
        turn(10)
    if key == "n":
        turn(-10)
    if key == "m":
        mission(1)
    if key == "s":
        mission(0)

win.bind_all("<Key>", keypressed)

# --- Boucle de réception non bloquante ---
def lire_rover():
    try:
        data = s.recv(1024).decode()
        for ligne in data.strip().splitlines():
            print("Rover :", ligne)
            if ligne.startswith("Orientation="):
                label_distance.config(text=ligne)
    except BlockingIOError:
        pass    # pas de données disponibles, c'est normal
    finally:
        win.after(100, lire_rover)   # ← rappel dans 100 ms

win.after(100, lire_rover)
win.mainloop()

s.close()