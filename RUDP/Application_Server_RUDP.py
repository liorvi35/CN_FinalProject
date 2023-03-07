
import socket


class Server:
    def __init__(self, address='localhost', port=5000, buffer_size=1024):
        self.address = address
        self.port = port
        self.buffer_size = buffer_size
        self.seq_num = 0
        self.ack_num = 0
        self.window_size = 4
        self.packets = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.address, self.port))

    def receive(self):
        while True:
            data, client_address = self.socket.recvfrom(self.buffer_size)
            packet = data.decode()
            seq_num, payload = packet.split('|')
            if int(seq_num) == self.ack_num:
                self.packets[int(seq_num)] = payload
                self.ack_num += 1
                while self.ack_num in self.packets:
                    self.ack_num += 1
            self.send_ack(client_address)

    def send_ack(self, client_address):
        ack = str(self.ack_num - 1) + '|ACK'
        self.socket.sendto(ack.encode(), client_address)

if __name__ == '__main__':
    server = Server()
    server.receive()
