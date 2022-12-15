import socket


class Client:

    def __init__(self, msg):
        # socket vars
        self.HEADER = 512
        self.PORT = 5050
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.SERVER = '192.168.4.1'
        self.ADDR = (self.SERVER, self.PORT)

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # commandlist and responselist (scan_lst)
        self.cmd_lst = msg
        self.scan_lst = [] # optimize if need be. Make an array of fixed size instead. Saves time as there is no need to realocate in memory
        
    def sock_connect(self):
        self.client_sock.connect(self.ADDR)

    def send_cmd_list(self):
        message = self.cmd_lst.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        # print(send_length)
        send_length += b' ' * (self.HEADER - len(send_length))
        # print(send_length)
        self.client_sock.send(send_length)
        self.client_sock.send(message)
        ans = self.client_sock.recv(2048).decode(self.FORMAT)
        self.scan_lst.append(ans)
        print(ans)
        return ans
    

    def send_keepalive(self):
        message = 'keepalive'.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client_sock.send(send_length)
        self.client_sock.send(message)
        print('keepalive sent')

    
    def recv_scan(self):
        ans = self.client_sock.recv(2048).decode(self.FORMAT)
        self.scan_lst.append(ans)
        print(ans)
        return ans

    def close(self):
        self.client_sock.close()


if __name__ == '__main__':
    try:
        msg = 'cmd_lst, command, battery?, takeoff, forward 100, forward 100'
        client = Client(msg=msg)
        client.sock_connect() 

        client.send_cmd_list()

        scan_amount = len(client.cmd_lst.split(',')) - 3 # because of 'cmd_lst, command,......., land'
        
        for scan_num in range(scan_amount):
            client.recv_scan()

        print(len(client.scan_lst), scan_amount)

        client.close()
        print("done closing")
    except Exception as e:
        print(e)
        client.close()
        print('done closing')