import socket 

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect(('localhost', 444))
print("Connected! ")

while True:
    da = input("Data à envoyer: ").encode()
    socket.send(da)
    if da == b"q":
        break
    
    dataRaw = socket.recv(255)
    data = dataRaw.decode()
    print("Reçu :",data)

socket.close()