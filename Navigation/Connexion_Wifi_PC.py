import socket
import json

PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

print("En attente de données...")

while True:
    print("TEST")
    data, addr = sock.recvfrom(4096)
    print("PLAY")
    message = data.decode()
    print("FUN")
    coo = json.loads(message)
    print("Reçu :", coo)