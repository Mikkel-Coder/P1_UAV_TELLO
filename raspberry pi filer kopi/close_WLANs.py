import network
import socket

ap = network.WLAN(network.AP_IF)
ap.active(True)

sta = network.WLAN(network.STA_IF)
sta.active(True)

while ap.active == False or sta.active == False:
    pass

print(ap.ifconfig())

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.close()


sta.disconnect()
ap.disconnect()

sta.active(False)
ap.active(False)

print('done')