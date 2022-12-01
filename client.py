import socket


class Client:

    def __init__(self):
        # socket vars
        self.HEADER = 64
        self.PORT = 5050
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.SERVER = '192.168.4.1'
        self.ADDR = (self.SERVER, self.PORT)

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # commandlist and responselist (scan_lst)
        self.cmd_lst = ''
        self.scan_lst = []
        
    def sock_connect(self):
        self.client_sock.connect(self.ADDR)

    def send_cmd_list(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        print(send_length)
        send_length += b' ' * (self.HEADER - len(send_length))
        print(send_length)
        self.client_sock.send(send_length)
        self.client_sock.send(message)
        print(self.client_sock.recv(2048).decode(self.FORMAT))

    
    def recv_scan(self):
        # scan_amount = len(self.cmd_lst.split(',')) - 3 # because of 'cmd_lst, command,......., land'
        # for scan in scan_amount:
        self.scan_lst.append(self.client_sock.recv(2048).decode(self.FORMAT))


if __name__ == '__main__':
    client = Client()
    client.sock_connect() 

    client.send_cmd_list('Hello there')

    scan_amount = len(client.cmd_lst.split(',')) - 3 # because of 'cmd_lst, command,......., land'
    for scan_num in range(scan_amount):
        client.recv_scan()

    print(client.scan_lst)
    