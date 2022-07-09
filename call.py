from socket import socket

with open('request.txt', 'rb') as fp:
    data = fp.read()

sock = socket()
sock.connect(('192.168.1.14', 8080))
sock.sendall(data)

chunks = []
for chunk in iter(lambda: sock.recv(1024), b''):
    chunks.append(chunk)

reply = b''.join(chunks)
print(reply.decode())