
# Importation de la lib socket
import socket

# Création de l'objet socket
s = socket.socket()
print("Connexion au pico...")
s.connect(('192.168.4.1', 8080))
print("Pico connecté !")


while True:
    d = input("Data à envoyer : ").encode()
    s.send(d)
    print(s.recv(1024))
    if d == b"q":
        print("Break")
        break
s.close()