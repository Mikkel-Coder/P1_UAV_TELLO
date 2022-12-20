import socket
import network
import time
from tello import Tello
from gpsclass import GPS_Class

# creating variables for the server
HEADER = 2048
FORMAT = 'utf-8'
PORT = 5050
DISCONNECT_MESSAGE = '!DISCONNECT'

# creating socket and accespoint
serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ap = network.WLAN(network.AP_IF)
# ap.ifconfig(('192.168.4.1','255.255.255.0','192.168.4.1', '8.8.8.8')) # sets the ip of the network
ap.active(True)
while ap.active == False:
            pass
        
print(ap.ifconfig()) # prints the networks IP among other things
ap_ip = ap.ifconfig()[0] # the IP is the first in the list
        
addr = (ap_ip, PORT)
print(f'Access point active with addr: {addr}')
serv_sock.bind(addr) # binds the socket to the server network via IP and PORT

serv_sock.listen() # listens until it gets a connection
print('listening on ', addr)

conn_pc, addr_pc = serv_sock.accept()

print(conn_pc)
print(addr_pc)
    