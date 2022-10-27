"""
THIS SCRIPT IS ONLY FOR USE TO CHANGE THE SSID AND PASSWORD ON THE TELLO DRONE! 
You must be connected to the drone before changing the SSID and password.
The SSID and password are both located in the config.ini file under [WIFI].

Ex of config.ini
_________________________
1: [WIFI]
2: ssid = YourSSIDHere
3: password = YourPassword

"""

from djitellopy import Tello
from configparser import ConfigParser
tello = Tello()
tello.connect()
config_object = ConfigParser()
config_object.read('config.ini')
wifi_logon_info = config_object['WIFI']
print('SSID:     {}'.format(wifi_logon_info['ssid']))
print('Password: {}'.format(wifi_logon_info['password']))
answer = None
while answer not in ('y', 'n'):
    answer = input('Do you wish to change? y/n\n')
    if answer == 'n':
        exit()
    elif answer == 'y':
        pass
    else:
        print('Invalid input!')
tello.set_wifi_credentials(wifi_logon_info['ssid'], wifi_logon_info['password'])
