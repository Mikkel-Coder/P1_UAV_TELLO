from djitellopy import Tello
import atexit, time
from dev import Tools


tello = Tello()

Tools.kill_switch(tello)
atexit.register(Tools.kill_switch, self = tello)



tello.connect()
tello.is_flying = True
tello.takeoff()
print('tryk nu!!')
time.sleep(1)
tello.land()
