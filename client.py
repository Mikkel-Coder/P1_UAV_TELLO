import socket


class Client:
    """
    Class for communicating with the Pico W server from the Client PC via sockets.
    """

    def __init__(self, msg):

        ## ---------------- Socket variables ----------------
        self.HEADER = 512 # data package
        self.PORT = 5050
        self.FORMAT = 'utf-8' # format for encoding and decoding data packages
        self.DISCONNECT_MESSAGE = '!DISCONNECT'
        self.SERVER = '192.168.4.1' # static ip adress
        self.ADDR = (self.SERVER, self.PORT)

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creates a socket via ipv4 and TCP

        ## ---------------- commandlist and responselist (scan_lst) ----------------
        self.cmd_lst = msg
        self.scan_lst = [] # for log
        

    def sock_connect(self) -> None:
        """
        Connect to the server.
        """
        self.client_sock.connect(self.ADDR)


    def send_cmd_list(self) -> str:
        """
        Sends the command list to the Pico W and expects an answers. Returns said answer 'ans'
        
        Inputs:
        ---
        - self

        Returns:
        ---
        - The response from the server.
        
        """
        message = self.cmd_lst.encode(self.FORMAT) # create message

        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length)) # data to be send
        
        self.client_sock.send(send_length) # tells the server what the length of the incoming message is

        self.client_sock.send(message) # sends the message/command list
        
        ans = self.client_sock.recv(2048).decode(self.FORMAT) # receives answer and decodes it
        
        self.scan_lst.append(ans)
        
        return ans
    

    def send_keepalive(self) -> None:
        """ Send keepalive to the Pico W. """

        message = 'keepalive'.encode(self.FORMAT)

        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))

        self.client_sock.send(send_length)
        
        self.client_sock.send(message)

    
    def recv_scan(self) -> str:
        """
        Saves a response from the Pico W in ans 

        Returns:
        ---
        - ans as a string with the Pico W response

        """

        ans = self.client_sock.recv(2048).decode(self.FORMAT)
        self.scan_lst.append(ans)
        
        return ans


    def close(self) -> None:
        """ Closes the socket. """
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