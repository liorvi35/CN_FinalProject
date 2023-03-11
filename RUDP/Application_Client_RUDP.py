import socket
import time

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
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize variables for sequence numbers, window size, and packets buffer
seq_num = 1
expe_ack = 1
window_size = INITIAL_CWND
packets_buffer = {}

# Send packets
for i in range(PACKET_COUNT):
    # Create packet
    time.sleep(1)
    print(f'i is: {i}')
    packet = f'{seq_num}:{i+1}'.encode()

    # Add packet to buffer
    packets_buffer[seq_num] = packet

    # Send packet
    client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
    print(f'Sent packet {seq_num}')

    # Update sequence number
    seq_num += 1
    client_socket.settimeout(TIMEOUT)

    # Wait for ACKs
    while True:
        # Receive ACK
        try:
            ack_packet, server_address = client_socket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            # Timeout, retransmit unacknowledged packets
            print('Timeout, retransmitting packets')
            window_size = max(window_size / 2, 1)
            expe_ack -= 1
            print(f'seq_num{seq_num} , packet{packet} , packets_buffer{packets_buffer.items()} ')
            for seq_num, packet in packets_buffer.items():
                client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
                print(f'Retransmitted packet {seq_num}')
            break

        # Parse ACK
        ack_data = ack_packet.decode()
        ack_seq_num = int(ack_data.split(':')[0])
        print(f'Received ACK {ack_seq_num}')

        """
        print(f'ack_seq_num: {ack_seq_num} expe_ack: {expe_ack} ')
        if(ack_seq_num != expe_ack):
            ack_seq_num += 1
            window_size = max(window_size / 2, 1)
            while ack_seq_num != expe_ack:
                packet = packets_buffer[ack_seq_num]
                client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))
                ack_packet, server_address = client_socket.recvfrom(BUFFER_SIZE)
                ack_data = ack_packet.decode()
                ack_seq_num_new = int(ack_data.split(':')[0])
                print(f'Received ACK {ack_seq_num_new}')
                if ack_seq_num_new == ack_seq_num + 1:
                    ack_seq_num += 1

        expe_ack += 1
        """
        # Update packets buffer
        if ack_seq_num in packets_buffer:
            del packets_buffer[ack_seq_num]

        # Update window size and threshold
        if len(packets_buffer) == 0:
            if window_size < THRESHOLD:
                # Slow start phase
                window_size *= 2
            else:
                # Congestion avoidance phase
                window_size += 1 / window_size
            break

    # Update window size
    if len(packets_buffer) == WINDOW_SIZE:
        window_size = max(window_size / 2, 1)

    client_socket.settimeout(TIMEOUT)


# Close socket
client_socket.close()
