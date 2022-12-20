"""Modified script of the main.py to work without the Tello drone."""

import socket
import network
import time
import machine
from GPS_optimized import GPS_Class

class Server:
    """
    Server object for the Pico W. This class uses the Tello and GPS_Class
    from the other scripts in order to manage flying the drone and communication with
    the client PC.
    """
    
    def __init__(self):
        # ---------- creating socket vars ----------
        self.HEADER = 2048
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = None
        self.led_pin = machine.Pin("LED", machine.Pin.OUT)
        
        # ---------- creating access point vars ----------
        self.PORT = 5050
        self.ap = network.WLAN(network.AP_IF)
        
        # ---------- creating log-list and commands list ---------- 
        self.msg_log = []
        self.cmd_list = None
        self.gps = GPS_Class()
        
    def activate_ap(self):
        """ Ativate the AP. """
        self.ap.active(True)
        while self.ap.active == False:
            pass
        
    def bind_sock_to_addr(self):
        """ Binds the sockets together. """
        self.activate_ap()

        print(self.ap.ifconfig())
        
        ap_ip = self.ap.ifconfig()[0]
        self.addr = (ap_ip, self.PORT)
        print(f'Access point active with addr: {self.addr}')
        
        self.serv_sock.bind(self.addr)
        
    
    def serv_listen(self) -> object:
        """
        Makes the server listen for a connection, accept it and return a socket object for the client and its address.
        
        Returns:
        ---
        - A socket object and its address.
        """
        self.serv_sock.listen(1)
        print('listening on', self.addr)

        try:
            conn_pc, addr_pc = self.serv_sock.accept()
            print(f"client connected with {conn_pc, addr_pc}")
            return conn_pc, addr_pc
    
        except KeyboardInterrupt as e:
            print(e)
            self.ap.active(False)

        except OSError as e:
            print('OSError', e)
            self.ap.active(False)
            
    
    def handle_client(self, conn_pc):
        """
        Handles the client PC's messages and controls the drone based on what the client PC tells it to do.
        It also sends Wi-Fi scans and coordinates to the client PC every time they are made.
        
        Inputs:
        ---
        - conn_pc object as the client PC.
        - tello_object as the Tello drone.
        """
        try:
            connected = True

            while connected:
                msg_length = conn_pc.recv(self.HEADER).decode(self.FORMAT)

                if msg_length:
                    msg_length = int(msg_length)
                    msg = conn_pc.recv(msg_length).decode(self.FORMAT)

                    if msg == self.DISCONNECT_MESSAGE:
                        connected = False
                    
                    # the scanning and flying
                    elif msg[:7] == 'cmd_lst': # finding the command list
                        self.cmd_list = msg.split(',')
                        del self.cmd_list[0] # removing the 'cmd_lst' part of the list

                        for i in range(len(self.cmd_list)):
                            self.cmd_list[i] = self.cmd_list[i].strip()
                            
                        print(self.cmd_list)
                        
                        #GPS_coords_begin = [57.01477, 9.98668]
                        #add_num = 0.0001
                        for command in self.cmd_list:
                            if 'forward' in command or 'takeoff' in command:
                                
                                self.led_pin.value(0)
                                GPS_coords = False

                                while GPS_coords == False:
                                    GPS_coords = self.gps.getcoords() # returns coordinates or 'False'
                                    #GPS_coords_begin[0] = GPS_coords_begin[0] + add_num
                                    #GPS_coords_begin[1] = GPS_coords_begin[1] + add_num
                                    #GPS_coords = tuple(GPS_coords_begin)

                                    if not GPS_coords == False:
                                        print('Sending scan to client')
                                        conn_pc.sendall(f'{self.ap.scan()}, {GPS_coords}'.encode(self.FORMAT))
                                        self.led_pin.value(1)
                                        time.sleep(1)
                                        
                                        
                                    else:
                                        print('Timed out. Getting coordinates again')
                                        conn_pc.send('keepalive'.encode(self.FORMAT))
                                        msg_length = conn_pc.recv(self.HEADER).decode(self.FORMAT)

                                        if msg_length:
                                            msg = conn_pc.recv(self.HEADER).decode(self.FORMAT)
                                               
                
            conn_pc.close()
            print('closing connection to pc')
            self.led_pin.value(0)
            
        except KeyboardInterrupt as e: 
            print(e)
            # closing everything
            conn_pc.close()
            print('closing connection to pc')
            self.led_pin.value(0)
            
            print("done closing")

if __name__ == '__main__':
    try:
        ap = Server()
        ap.bind_sock_to_addr()
        ap.serv_sock.settimeout(600.0)

        conn_pc, addr_pc = ap.serv_listen()
        ap.led_pin.value(1)
        
        ap.handle_client(conn_pc)

        print(ap.msg_log)
        
        conn_pc.close()
        ap.serv_sock.close()
        ap.ap.disconnect()
        ap.ap.active(False)
        
    except KeyboardInterrupt as a:
        print(a)
        # closing everything
        conn_pc.close()
        ap.serv_sock.close()
        ap.ap.disconnect()
        ap.ap.active(False)
        print("done closing")
        
    except OSError as e:
        print(e)
        ap.serv_sock.close()
        ap.ap.disconnect()
        ap.ap.active(False)
        print('closed server')
        