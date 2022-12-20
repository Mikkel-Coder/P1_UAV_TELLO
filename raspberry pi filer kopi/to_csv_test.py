import machine
import utime

import time
import network
import ubinascii


led_pin = machine.Pin("LED", machine.Pin.OUT)

time_start = utime.time()

sleep_time = 0.2 # time between blinks
time_till_start = 3 # seconds before starting the actual script. Will take more like double this due to processing in the meantime and sleeping twice
n_cycles = int(time_till_start/ 2 / sleep_time) # deviding by 2 as there are 2 sleeps per cycle

for i in range(n_cycles):
    led_pin.value(1) # powers LED
    utime.sleep(sleep_time)
    led_pin.value(0)
    utime.sleep(sleep_time)

time_stop = utime.time()

time_taken = time_stop - time_start
print(f"time before measurements began was ~ {time_taken} seconds. {n_cycles} cycles of blinks were run")

led_pin.value(1) # powers LED after being done. Indicates the actual script is running now.

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# measuring
measurements = 20
time_between_measurements = 2
measure_dict = {}
for i in range(measurements):
    measure_dict[i] = [wlan.scan(), time.time()]
    time.sleep(time_between_measurements)

measure_times = []
for i in range(measurements):
    measure_times.append(measure_dict[i][-1]) # saving the timestamps of the measurements without the last two parts (weekday and yearday)
    measure_dict[i] = measure_dict[i][0:-1] # esentialy deletes the timestamps from the dict

file = open("measured_data.csv","w") # creating/overwriting csvfile
file.write("ssid"+";"+"bssid"+";"+"channel"+";"+"RSSI"+";"+"security"+";"+"hidden"+";"+"time"+"\n") # creating column-names
for i in range(measurements):
    for aps in measure_dict[i]:
        for ap in aps:
            file.write(f'{ap[0]}'+";"+f'{ap[1]}'+";"+f'{ap[2]}'+";"+f'{ap[3]}'+";"+f'{ap[4]}'+";"+f'{ap[5]}'+";"+f'{measure_times[i]}' + "\n")
file.close()
led_pin.value(0) # turns off LED when script is done

# print(measure_times[1] - measure_times[0])
