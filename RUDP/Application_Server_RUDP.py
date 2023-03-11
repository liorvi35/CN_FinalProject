import socket
import time
import random

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 1234
BUFFER_SIZE = 1024
WINDOW_SIZE = 4
PACKET_COUNT = 20
INITIAL_CWND = 1
THRESHOLD = 8
TIMEOUT = 3

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Initialize variables for sequence numbers, window size, and packets buffer
seq_num = 1
window_size = INITIAL_CWND
packets_buffer = {}
received = {}

# Define a function to send ACKs
def send_ack(seq_num, num_acks=1):
    # Check if the ACK is a duplicate
    if seq_num in received and received[seq_num] == num_acks:
        # Increment the counter for the sequence number
        received[seq_num] += 1
        # If the counter reaches a threshold, assume packet loss and retransmit the packet
        if received[seq_num] == 3:
            # Retransmit the packet
            server_socket.sendto(packets_buffer[seq_num], client_address)
            print(f'Retransmitted packet {seq_num}')
            # Reset the counter for the sequence number
            received[seq_num] = 0
    else:
        # Send the ACK
        ack_packet = f'{seq_num}:ACK'.encode()
        print(f'send: {ack_packet}')
        server_socket.sendto(ack_packet, client_address)
        # Update the received dictionary with the number of ACKs received for the sequence number
        received[seq_num] = num_acks


# Receive packets
while True:
    # Receive packet
    #print(packets_buffer)
    packet, client_address = server_socket.recvfrom(BUFFER_SIZE)
    packet_data = packet.decode()
    print(packet_data)
    packet_seq_num = int(packet_data.split(':')[0])
    print(f'Received packet {packet_seq_num}')

    # Add packet to buffer
    packets_buffer[packet_seq_num] = packet

    # Send ACK for received packet
    send_ack(packet_seq_num)

    # Update received dictionary
    received[packet_seq_num] = True

    print(f'packets_buffer.get(seq_num): {packets_buffer.get(seq_num)} seq_num: {seq_num} window_size: {window_size} len(received) % WINDOW_SIZE: {len(received) % WINDOW_SIZE}')


    # Check if there are packets in the buffer that can be delivered
    while packets_buffer.get(seq_num) and seq_num <= window_size:
        # Deliver packet
        delivered_packet = packets_buffer.pop(seq_num)
        print(f'Delivered packet {seq_num}')
        # Update sequence number
        seq_num += 1

    # Update window size and threshold
    if len(received) % WINDOW_SIZE == 1 or len(received) % WINDOW_SIZE == 0:
        # Update window size and threshold based on ACKs
        if window_size < THRESHOLD:
            # Slow start phase
            window_size *= 2
        else:
            # Congestion avoidance phase
            window_size += 1 / window_size
        # Reset received dictionary
        received = {}
    elif len(packets_buffer) == WINDOW_SIZE:
        # Timeout, retransmit unacknowledged packets
        print('Timeout, retransmitting packets')
        window_size = max(window_size / 2, 1)
        for seq_num, packet in packets_buffer.items():
            server_socket.sendto(packet, client_address)
            print(f'Retransmitted packet {seq_num}')
        # Reset received dictionary
        received = {}
    # Set timeout for next packet
    #server_socket.settimeout(TIMEOUT)
