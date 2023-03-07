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
        self.socket.settimeout(1.0)

    def send(self, messages):
        for message in messages:
            packets = self.create_packets(message)
            num_packets = len(packets)
            acks = [False] * num_packets
            while not all(acks):
                window_start = self.seq_num
                window_end = min(self.seq_num + self.window_size, num_packets)
                for i in range(window_start, window_end):
                    if not acks[i]:
                        packet = packets[i]
                        self.socket.sendto(packet.encode(), (self.address, self.port))
                try:
                    data, server_address = self.socket.recvfrom(self.buffer_size)
                except socket.timeout:
                    continue
                else:
                    seq_num, ack = data.decode().split('|')
                    if int(seq_num) >= self.seq_num and ack == 'ACK':
                        acks[int(seq_num)] = True
                        while self.seq_num < num_packets and acks[self.seq_num]:
                            self.seq_num += 1

    def create_packets(self, message):
        packets = []
        for i in range(0, len(message), self.buffer_size - 5):
            seq_num = str(i // (self.buffer_size - 5))
            packet = seq_num + '|' + message[i:i + self.buffer_size - 5]
            packets.append(packet)
        return packets

if __name__ == '__main__':
    client = Client()
    messages = ['hello', 'world', 'how are you?']
    client.send(messages)
