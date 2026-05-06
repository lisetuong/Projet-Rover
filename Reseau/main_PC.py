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

def send_cmd(cmd):
    try:
        s.send(f"{cmd}\n".encode())
    except OSError:
        pass

def linear(distance_cm):
    send_cmd(f"move={distance_cm}")

def lateral(distance_cm):
    send_cmd(f"lateral={distance_cm}")

def turn(distance_cm):
    send_cmd(f"turn={distance_cm}")

def mission(statut):
    send_cmd(f"mission={statut}")

pressed_keys = set()

def keypressed(e):
    key = e.keysym
    if key == "Up":
        linear(10)
    if key == "Down":
        linear(-10)
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
    if key == "l":
        mission(0)
    
    if key in pressed_keys:
        return
    
    pressed_keys.add(key)
    
    if key == "z":
        send_cmd("forward")
    elif key == "s":
        send_cmd("backward")
    elif key == "d":
        send_cmd("right")
    elif key == "q":
        send_cmd("left")
    elif key == "a":
        send_cmd("turn_left")
    elif key == "e":
        send_cmd("turn_right")

def keyrelease(e):
    key = e.keysym
    if key in pressed_keys:
        pressed_keys.remove(key)
    if key in ("z", "s", "d", "q", "a", "e"):
        send_cmd("stop")

win.bind("<KeyPress>", keypressed)
win.bind("<KeyRelease>", keyrelease)

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