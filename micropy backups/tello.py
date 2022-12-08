import socket
import network
import time


class Tello:
    def __init__(self):
        # drone network vars
        self.tello_ssid = 'TELLO-gr155'
        self.tello_pass = 'wordpass'
        self.sta = network.WLAN(network.STA_IF)
        
        # Pico W client socket vars
        self.format = 'utf-8'
        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.tello_address = (self.tello_ip, self.tello_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        

    def conn_drone_wifi(self):
        self.sta.active(True)
        
        while self.sta.active == False:
            pass
        
        while self.sta.isconnected() == False:
            self.sta.connect(self.tello_ssid, self.tello_pass)
            print("client connected: ", self.sta.isconnected())
            time.sleep(5)

        print("connected STA to drone: ", self.sta)
        
    
    def drone_socket(self):
        # check if Pico W is connected to the drone via WiFi
        if self.sta.isconnected() == True:
            self.client_socket.bind(('', self.tello_port))
            
    
    def send(self, command):
        # see commands in Tello_SDK_3.0_User_Guide_en.pdf
        print(f'sending command: {command}')
        self.client_socket.sendto(str(command).encode(self.format), self.tello_address)
        
        response = self.client_socket.recv(1024).decode(self.format)
        print(response)
        time.sleep(0.5)
        return response
        
if __name__ == '__main__':        
    tello = Tello()

    tello.conn_drone_wifi()
    tello.drone_socket()
    print(tello.client_socket, tello.tello_address)

    # prøv at køre det her når I kan
    tello.send('command')

    tello.send('battery?')

    tello.send('takeoff')

    tello.send('speed?')

    tello.send('forward 50')

    tello.send('land')
    
    tello.sta.disconnect()
    tello.client_socket.close()
    tello.sta.active(False)
    
