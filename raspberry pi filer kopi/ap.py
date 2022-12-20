import socket
import network
import time

# creating the AP
HEADER = 2048
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
PORT = 5050
ap_ssid = "gr155"
ap_password = "123456789gr155"
ap = network.WLAN(network.AP_IF)
ap.config(essid=ap_ssid, password=ap_password) 
ap.active(True)

#creating the client/STAtion
PC_ssid = "LAPTOP8DPD0KSO3158"
PC_pass = "45H704nn"
sta = network.WLAN(network.STA_IF)
sta.active(True)

# making sure both are functioning before moving on
while ap.active == False or sta.active == False:
    pass

while sta.isconnected() == False:
    sta.connect(PC_ssid, PC_pass)
    print(sta.isconnected())
    time.sleep(5)

print("connected STA to pc: ", sta)

ap_ip = ap.ifconfig()[0]
print("Access point active with addr: ", ap_ip)

# creating a socket for the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ADDR = socket.getaddrinfo(ap_ip,PORT)[0][-1] # gets the format we want

server.bind(ADDR)
server.listen()

print('listening on', ADDR)

conn_pc, addr_pc = server.accept()

print("connected pc to AP with socket/addr: ", conn_pc,"/", addr_pc)
time.sleep(2)

# connections are established from here on, so this will be where all other code goes

"""Tænker noget struktur alla det her:
 - En liste af de commands der skal sendes til dronen
længden af den liste bruges så til at vide hvor mange gange der skal loopes
 - et loop med range(len(instruksliste)):
    - (wlan.scan, GPS coords) som så sendes til clienten
    - instruksliste[i] sendes så til dronen
            Lav noget logik der sørger for, at den er færdig med at flyve, før der scannes igen (hvis det ikke allerede findes)
            
Husk et script der connecter Pico clienten til dronen. - check"""

# forsøg på WLAN.scan() der så sendes til client

connected = True
while connected:
    msg_length = conn_pc.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn_pc.recv(msg_length).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
        
        print(f'[{addr_pc}] {msg}')
        # conn_pc.send('Message received'.encode(FORMAT))
        conn_pc.send(f'{ap.scan()}'.encode(FORMAT))

    conn_pc.close()



# closing after a few scans to prove a point
print(ap.isconnected())
print("ap scanner: ", ap.scan())
time.sleep(2)

print(sta.isconnected())
print("sta scanner: ", sta.scan())
time.sleep(2)
print("closing now...")

server.close()
ap.active(False)
