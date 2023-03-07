import socket
import random

class Client:
    def __init__(self, address='localhost', port=5000, buffer_size=1024):
        self.address = address
        self.port = port
        self.buffer_size = buffer_size
        self.window_size = 4
        self.seq_num = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        packets = self.create_packets(message)
        while True:
            window = packets[self.seq_num:self.seq_num + self.window_size]
            for i in range(len(window)):
                packet = window[i]
                self.socket.sendto(packet.encode(), (self.address, self.port))
            try:
                data, server_address = self.socket.recvfrom(self.buffer_size)
            except socket.timeout:
                continue
            else:
                seq_num, ack = data.decode().split('|')
                if int(seq_num) >= self.seq_num and ack == 'ACK':
                    self.seq_num = int(seq_num) + 1
                    if self.seq_num >= len(packets):
                        break

    def create_packets(self, message):
        packets = []
        for i in range(0, len(message), self.buffer_size - 5):
            seq_num = str(i // (self.buffer_size - 5))
            packet = seq_num + '|' + message[i:i + self.buffer_size - 5]
            packets.append(packet)
        return packets

if __name__ == '__main__':
    client = Client()
    client.send('hello')
