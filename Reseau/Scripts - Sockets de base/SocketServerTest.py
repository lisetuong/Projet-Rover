import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', 444))

print("Waiting for connection....")
socket.listen()
client, address = socket.accept()
print("{} connected".format(address))

while True:
    dataRaw = client.recv(255)
    data = dataRaw.decode()
    print("Reçu :",data)
    
    da = input("Data à envoyer: ").encode()
    client.send(da)
    if da == b"q":
        break