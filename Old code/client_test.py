import socket


HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = '192.168.4.1'
ADDR = (SERVER, PORT)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

print("connected!")

send("Hello, server!")
input()


cmd_list = "cmd_lst, command, takeoff,forward 150,forward 150,cw 90,forward 150,cw 90,forward 150,forward 150,land"
send(cmd_list)
input()

send(DISCONNECT_MESSAGE)
