import socket
import network
import time


class Tello:
    """API for controlling Tello drone"""
    
    def __init__(self):

        # ---------------- Drone network vars ----------------
        self.tello_ssid = 'TELLO-gr155'
        self.tello_pass = 'wordpass'
        self.sta = network.WLAN(network.STA_IF) # station aka router
        
         ## ---------------- Pico W client socket vars ----------------
        self.format = 'utf-8'
        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889 # from Tello SDK
        self.tello_address = (self.tello_ip, self.tello_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4 via UDP 
        

    def conn_drone_wifi(self) -> None:
        """ Connect to the Tello drones Wi-Fi. """
        self.sta.active(True)
        
        while self.sta.active == False:
            pass
        
        while self.sta.isconnected() == False:
            self.sta.connect(self.tello_ssid, self.tello_pass)
            print("client connected: ", self.sta.isconnected())
            time.sleep(5)

        print("connected STA to drone: ", self.sta)
        
    
    def drone_socket(self) -> None:
        """ Bind Pico W socket to the drones socket. """
        if self.sta.isconnected() == True: # check if Pico W is connected to the drone via WiFi
            self.client_socket.bind(('', self.tello_port))
            
    
    def send(self, command: str) -> str:
        """
        Sends command to Tello drone and receives answer.
        For docs on commands, see Tello_SDK_3.0_User_guide_en.pdf.
        
        Inputs:
        ---
        - command: a string command selected from the Tello SDK v3

        Returns:
        ---
        - The response from the Tello Drone.
        """

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

    tello.send('command')

    tello.send('battery?')

    tello.send('takeoff')

    tello.send('speed?')

    tello.send('forward 50')

    tello.send('land')
    
    tello.sta.disconnect()
    tello.client_socket.close()
    tello.sta.active(False)
    