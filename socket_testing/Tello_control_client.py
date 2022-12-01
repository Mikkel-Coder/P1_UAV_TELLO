"""
Overvejelser:
  - SKAL man forbinde raspi til Tello med wifi? eller kan det gøres udelukkende via socket?
    Det er vigtigt at vide, fordi WLAN.Scan() kun virker når man ikke er koblet til et netværk (så vidt vi ved)
  - virker WLAN.Scan() kun når man ikke er forbundet til et wifi/netværk?
  - Kan raspi aggere både server OG client? hvis ja, hvordan?

 - struktur:
    PC: client
    raspi: server AND client
    Tello: server / wifihotspot?
    PC <-> raspi <-> Tello, mens raspi også kan WLAN.Scan().

Hvad kan vi hvis Tello KRÆVER at man er forbundet via wifi?
Så kan vi vel ikke være på Tello fra raspi MENS vi bruger WLAN.Scan(). Man kan evt. kortvarigt disconnecte, scanne og så reconnecte.
Hvis det ikke kræves, er strukturen som set ovenfor.

Målet må være, at lave noget server/client på selve picoen på en fed måde, hvor de to kan coeksistere.
Et eksempel er pathfinding:
X og Y sendes til raspi fra PC (altså område der skal afsøges)
X og Y laves om til flyveinstrukser og stilles i kø
While True:
    WLAN.scan()
    gps angiver koordinater til punkt
    1 instruks sendes til drone
    Det hele lægges i en csv/ sendes tilbage til PC og lægges i csv eller livebehandles der.


Kan også laves med keyboard control hvor:
PC flyver drone
raspi scanner hver gang dens GPS koordinater er x centimeter fra sidste punkt
"""

from djitellopy import tello
import KeyPressModule as kp
from time import sleep


kp.init()
drone = tello.Tello()
drone.connect()
print(drone.get_battery())
# sleep(5)

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0 # lr = left/right, fb = forward/back, ud = up/down, dv = yaw velocity
    speed = 50 # cm/second

    if kp.getKey('LEFT'): lr = -speed
    elif kp.getKey('RIGHT'): lr = speed

    if kp.getKey('UP'): fb = speed
    elif kp.getKey('DOWN'): fb = -speed

    if kp.getKey('w'): ud = speed
    elif kp.getKey('s'): ud = -speed

    if kp.getKey('a'): yv = -speed * 2
    elif kp.getKey('d'): yv = speed * 2

    if kp.getKey('q'): drone.land()
    if kp.getKey('e'): drone.takeoff()

    return [lr, fb, ud, yv]

while True:
    vals = getKeyboardInput()
    drone.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)
