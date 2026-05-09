import socket
import tkinter as tk
import math

# --- Connexion au rover ---
s = socket.socket()
s.connect(('192.168.4.1', 8080))
s.setblocking(False)          # ← clé : recv() ne bloque plus

# --- Interface Tkinter ---
win = tk.Tk()
win.title("Contrôle Rover")
main_frame = tk.Frame(win)
main_frame.pack()

# Panneau touches
panel = tk.Frame(main_frame)
panel.pack(side="left", padx=10, pady=10)

# Canvas carte
canvas = tk.Canvas(main_frame, width=600, height=600, bg="white")
canvas.pack(side="right")

trajet = [(0, 0)]
orientation = 90

def touche(parent, texte):
    label = tk.Label(
        parent,
        text=texte,
        width=6,
        height=3,
        relief="solid",
        font=("Arial", 12, "bold")
    )
    return label

# CONTROLE CONTINU
titre1 = tk.Label(panel, text="Contrôle continu", font=("Arial", 14, "bold"))
titre1.pack(pady=5)

frame_continu = tk.Frame(panel)
frame_continu.pack(pady=5)

touche(frame_continu, "A").grid(row=0, column=0, padx=2, pady=2)
touche(frame_continu, "Z").grid(row=0, column=1, padx=2, pady=2)
touche(frame_continu, "E").grid(row=0, column=2, padx=2, pady=2)

touche(frame_continu, "Q").grid(row=1, column=0, padx=2, pady=2)
touche(frame_continu, "S").grid(row=1, column=1, padx=2, pady=2)
touche(frame_continu, "D").grid(row=1, column=2, padx=2, pady=2)

# CONTROLE PAS A PAS
titre2 = tk.Label(panel, text="Pas à pas", font=("Arial", 14, "bold"))
titre2.pack(pady=15)

frame_pas = tk.Frame(panel)
frame_pas.pack(pady=5)

touche(frame_pas, "B").grid(row=0, column=0, padx=2, pady=2)
touche(frame_pas, "↑").grid(row=0, column=1, padx=2, pady=2)
touche(frame_pas, "N").grid(row=0, column=2, padx=2, pady=2)

touche(frame_pas, "←").grid(row=1, column=0, padx=2, pady=2)
touche(frame_pas, "↓").grid(row=1, column=1, padx=2, pady=2)
touche(frame_pas, "→").grid(row=1, column=2, padx=2, pady=2)

# MISSION
titre3 = tk.Label(panel, text="Mission", font=("Arial", 14, "bold"))
titre3.pack(pady=15)

frame_mission = tk.Frame(panel)
frame_mission.pack(pady=5)

touche(frame_mission, "M").grid(row=0, column=0, padx=5, pady=5)
touche(frame_mission, "L").grid(row=0, column=1, padx=5, pady=5)

# INFOS ROVER
titre4 = tk.Label(panel, text="État Rover", font=("Arial", 14, "bold"))
titre4.pack(pady=15)

infos_frame = tk.Frame(panel, relief="solid", bd=1)
infos_frame.pack(pady=5, fill="x")

label_orientation = tk.Label(
    infos_frame,
    text="Orientation : 90°",
    font=("Arial", 12),
    anchor="w"
)
label_orientation.pack(fill="x", padx=5, pady=5)

label_position = tk.Label(
    infos_frame,
    text="Position : (0 ; 0)",
    font=("Arial", 12),
    anchor="w"
)
label_position.pack(fill="x", padx=5, pady=5)

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

def world_to_screen(x, y, min_x, min_y, scale, offset_x, offset_y):

    sx = (x - min_x) * scale + offset_x
    sy = 600 - ((y - min_y) * scale + offset_y)

    return sx, sy

def draw_rover(x, y, angle_deg):
    """
    Dessine une flèche orientée
    """
    size = 15

    angle_rad = math.radians(angle_deg)

    # Pointe avant
    x1 = x + size * math.cos(angle_rad)
    y1 = y - size * math.sin(angle_rad)

    # Arrière gauche
    x2 = x + size * math.cos(angle_rad + 2.5)
    y2 = y - size * math.sin(angle_rad + 2.5)

    # Arrière droite
    x3 = x + size * math.cos(angle_rad - 2.5)
    y3 = y - size * math.sin(angle_rad - 2.5)

    canvas.create_polygon(
        x1, y1,
        x2, y2,
        x3, y3,
        fill="red"
    )

def redraw():
    canvas.delete("all")
    if len(trajet) < 1:
        return

    xs = [p[0] for p in trajet]
    ys = [p[1] for p in trajet]
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    largeur = max_x - min_x
    hauteur = max_y - min_y

    if largeur < 1:
        largeur = 1
    if hauteur < 1:
        hauteur = 1

    margin = 50
    scale_x = (600 - 2 * margin) / largeur
    scale_y = (600 - 2 * margin) / hauteur
    scale = min(scale_x, scale_y)

    offset_x = (600 - largeur * scale) / 2
    offset_y = (600 - hauteur * scale) / 2

    points = []
    for x, y in trajet:
        sx, sy = world_to_screen(
            x, y,
            min_x, min_y,
            scale,
            offset_x,
            offset_y
        )
        points.extend([sx, sy])

    if len(points) >= 4:
        canvas.create_line(points, fill="blue", width=2)
    x, y = trajet[-1]
    sx, sy = world_to_screen(
        x, y,
        min_x, min_y,
        scale,
        offset_x,
        offset_y)

    draw_rover(sx, sy, orientation)

# --- Boucle de réception non bloquante ---
def lire_rover():
    global trajet, orientation
    try:
        data = s.recv(1024).decode()
        for ligne in data.strip().splitlines():
            print("Rover :", ligne)
            try:
                morceaux = ligne.split(",")
                data = {}
                for m in morceaux:
                    key, value = m.split("=")
                    data[key] = float(value)

                x = data["X"]
                y = data["Y"]
                orientation = data["Orientation"]
                label_orientation.config(text=f"Orientation : {orientation:.1f}°")
                label_position.config(text=f"Position : ({x:.1f} ; {y:.1f})")
                if trajet[-1] != (x, y):
                    trajet.append((x, y))

            except Exception as e:
                print("Erreur réception :", e)
        redraw()
    except BlockingIOError:
        pass    # pas de données disponibles, c'est normal
    finally:
        win.after(100, lire_rover)   # ← rappel dans 100 ms

redraw()
win.after(100, lire_rover)
win.mainloop()

s.close()