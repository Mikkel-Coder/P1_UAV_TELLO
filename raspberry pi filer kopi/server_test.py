import socket
import network
import time

class Server:
    
    def __init__(self):
        # creating socket vars
        self.HEADER = 2048
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = None
        
        # creating access point vars
        self.PORT = 5050
        self.ap = network.WLAN(network.AP_IF)
        self.ap.config(ssid="gr155-PicoW", password="123456789")
        
        # creating log-list and commands list
        self.msg_log = []
        self.cmd_list = None
        
    def activate_ap(self):
        self.ap.active(True)
        while self.ap.active == False:
            pass
        
    def bind_sock_to_addr(self):
        self.activate_ap()
        # self.ap.ifconfig()
        self.ap.ifconfig(('192.168.4.4','255.255.255.0','192.168.4.1', '8.8.8.8'))
        self.addr = (self.ap.ifconfig()[0], self.PORT)
        print(f'Access point active with addr: {self.addr}')
        self.serv_sock.bind(self.addr)
        
    
    def serv_listen(self):
        self.serv_sock.listen()
        print('listening on', self.addr)
        try:
            conn_pc, addr_pc = self.serv_sock.accept()
            print(f"client connected with {conn_pc, addr_pc}")
            return conn_pc, addr_pc
    
        except KeyboardInterrupt as e:
            print(e)
            self.ap.active(False)
            while self.ap.active == True:
                pass
        except OSError as e:
            print('OSError', e)
            self.ap.active(False)
            while self.ap.active == True:
                pass
            
    
    def handle_client(self, conn_pc, addr_pc):
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
                            if 'forward' in command or 'takeoff' in command:
                                conn_pc.send(f'{self.ap.scan()}')
                                               
                
                print(f'[{addr_pc}] {msg}')
                conn_pc.send('Message received'.encode(self.FORMAT))
                
                self.msg_log.append(msg)
                
            # closing everything
            conn_pc.close()
            self.serv_sock.close()
            self.ap.disconnect()
            self.ap.active(False)
            
        except KeyboardInterrupt as e: # virker ikke lige nu når dronen ikke får sendt svar retur
            print(e)
            # closing everything
            conn_pc.close()
            self.serv_sock.close()
            self.ap.disconnect()
            self.ap.active(False)
                    
            print("done closing")
            # måske noget kode her der også logger fejlbeskeder og måske self.msg_log


if __name__ == '__main__':
    try:
        ap = Server()
        ap.bind_sock_to_addr()

        conn_pc, addr_pc = ap.serv_listen()
        
        ap.handle_client(conn_pc, addr_pc)

        print(ap.msg_log)
        
        conn_pc.close()
        ap.serv_sock.close()
        ap.ap.disconnect()
        ap.ap.active(False)
        
    except KeyboardInterrupt as a: # virker ikke lige nu når dronen ikke får sendt svar retur
        print(a)
        # closing everything
        # conn_pc.close()
        ap.serv_sock.close()
        ap.ap.disconnect()
        ap.ap.active(False)
        
        print("done closing") 

