import socket
import network
import time
import machine
from tello import Tello
from GPS_optimized import GPS_Class

class Server:
    
    def __init__(self):
        # creating socket vars
        self.HEADER = 2048
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = None
        
        # creating LED var
        self.led_pin = machine.Pin("LED", machine.Pin.OUT)
        
        # creating access point vars
        self.PORT = 5050
        self.ap = network.WLAN(network.AP_IF)
        # self.ap.config(ssid="gr155-PicoW", password="gr15512345")
        
        # creating log-list and commands list
        self.msg_log = []
        self.cmd_list = None
        self.gps = GPS_Class()
        
    def activate_ap(self):
        self.ap.active(True)
        while self.ap.active == False:
            pass
        
    def bind_sock_to_addr(self):
        self.activate_ap()
        # self.ap.ifconfig()
        # self.ap.ifconfig(('192.168.4.2','255.255.255.0','192.168.4.1', '8.8.8.8'))
        print(self.ap.ifconfig())
        ap_ip = self.ap.ifconfig()[0]
        self.addr = (ap_ip, self.PORT)
        print(f'Access point active with addr: {self.addr}')
        self.serv_sock.bind(self.addr)
        
    
    def serv_listen(self):
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
            
    
    def handle_client(self, conn_pc, addr_pc, tello_object):
        # also takes a tello-object so the killswitch will work by sending 'emergency' or 'land' to the drone
        # by breaking the connection from the PC client, an error is thrown in the try-except, which then lands the drone
        # This is a bit janky, but way easier to implement than threading, which we haven't learned
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
                        
                        # conn_pc.send(f'{self.ap.scan()}, "GPS coords"')
                        for command in self.cmd_list:
                            tello_object.send(command)
                            if 'forward' in command or 'takeoff' in command:
                                
                                # old gps code. Stays as the client side is built to receive data with coordinates even though they aren't used.
                                self.led_pin.value(0)
                                GPS_coords = False
                                while GPS_coords == False:
                                    # GPS_coords = self.gps.getcoords() # returns coordinates or 'False'
                                    GPS_coords = (57.01477, 9.98668)
                                    if not GPS_coords == False:
                                        print('Sending scan to client')
                                        conn_pc.sendall(f'{self.ap.scan()}, {GPS_coords}'.encode(self.FORMAT))
                                        self.led_pin.value(1)
                                        time.sleep(2)
                                        
                                    else:
                                        tello_object.send('stop') # if timeout of 5 secs is reached, the drone recieves a command, keeping it alive.
                                        print('Timed out. Sending "stop" to drone and getting coordinates again')
                                        conn_pc.send('keepalive'.encode(self.FORMAT))
                                        msg_length = conn_pc.recv(self.HEADER).decode(self.FORMAT)
                                        if msg_length:
                                            msg = conn_pc.recv(self.HEADER).decode(self.FORMAT)
                                        # add client ping in order to do proper killswitch
                                        
                                        # It would autoland after 15 secs
                                               
                
                print(f'[{addr_pc}] {msg}')
                # conn_pc.sendall('Message received'.encode(self.FORMAT))
                
                self.msg_log.append(msg)
                self.led_pin.value(0)
                
            # closing everything
            conn_pc.close()
            print('closing connection to pc')
            # self.serv_sock.close()
            # self.ap.disconnect()
            # self.ap.active(False)
            
        except KeyboardInterrupt as e:
            print(e)
            # closing everything
            conn_pc.close()
            print('closing connection to pc')
            self.led_pin.value(0)
            
            tello_object.send('land')
            print("done closing")
        except IndexError as e:
            tello_object.send('land')
            conn_pc.close()
            self.led_pin.value(0)


if __name__ == '__main__':
    try:
        tello = Tello()

        ap = Server()
        ap.bind_sock_to_addr()
        ap.serv_sock.settimeout(600.0)
        
        tello.conn_drone_wifi()
        tello.drone_socket()

        conn_pc, addr_pc = ap.serv_listen()
        ap.led_pin.value(1)
        
        ap.handle_client(conn_pc, addr_pc, tello)

        print(ap.msg_log)
        
        conn_pc.close()
        ap.serv_sock.close()
        ap.ap.disconnect()
        ap.ap.active(False)
        
        tello.sta.disconnect()
        tello.client_socket.close()
        tello.sta.active(False)
        
    except KeyboardInterrupt as a: # virker ikke lige nu når dronen ikke får sendt svar retur
        print(a)
        # closing everything
        conn_pc.close()
        ap.serv_sock.close()
        ap.ap.disconnect()
        ap.ap.active(False)
        print('Closed server')
        
        tello.send('land')
        
        tello.sta.disconnect()
        tello.client_socket.close()
        tello.sta.active(False)
        print('closed tello socket and WiFi station')
        
    except OSError as e:
        print(e)
        ap.serv_sock.close()
        ap.ap.disconnect()
        ap.ap.active(False)
        conn_pc.close()
        print('Closed server')
        
        tello.send('land')
        
        tello.sta.disconnect()
        tello.client_socket.close()
        tello.sta.active(False)
        print('closed tello socket and WiFi station')
        
