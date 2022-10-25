from djitellopy import Tello
import atexit, time
from dev import tools

tello = Tello()

tools.kill_switch(tello)
atexit.register(tools.kill_switch, self = tello)



tello.connect()
tello.is_flying = True
tello.takeoff()
print('tryk nu!!')
time.sleep(1)
tello.land()
