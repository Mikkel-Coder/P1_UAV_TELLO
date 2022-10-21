from djitellopy import Tello
from time import sleep

tello = Tello()

tello.connect()
print(tello.get_battery())

tello.takeoff()
sleep(1)
tello.land()

# lav en kill switch (kig på python event. noget med script-end agtigt. Søg på det)
# sæt altid propeller på på den rigtige måde. Se appen for hjælp.

# download appen.

# lav struktur der kan generere ruter, så man kan smide et område ind, og så laver den selv en rute.
