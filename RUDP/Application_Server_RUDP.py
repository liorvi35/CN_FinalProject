import json
import pickle
import socket
import time
import random

import Application_Queries
import firebase_admin
from firebase_admin import credentials
from datetime import datetime  # for time and data

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 1235
BUFFER_SIZE = 1024
WINDOW_SIZE = 4
PACKET_COUNT = 20
INITIAL_CWND = 1
THRESHOLD = 8
TIMEOUT = 3

cred = credentials.Certificate("FireBase_SDK.json")
print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] opened database's credentials")

firebase_admin.initialize_app(cred, {"databaseURL": "https://cn-finalproject-default-rtdb.firebaseio.com/"})
print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] connected to database")

obj = Application_Queries.FirebaseQueries()

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Initialize variables for sequence numbers, window size, and packets buffer
seq_num = 1
window_size = INITIAL_CWND
packets_buffer = {}
received = {}
last_seq = 0


def handle_data(data):
    obj = Application_Queries.FirebaseQueries()
    num = int(data.split('$')[0])

    if num == 1:  # add new student
        #student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
        #Application_Queries.FirebaseQueries.add_new_student(obj, student_data)
        #client_sock.sendall(f"Student with id = {student_data[1]} was added to database!".encode())
        string_after_first_dollar = data.split('$')[1:]
        Application_Queries.FirebaseQueries.add_new_student(obj, string_after_first_dollar)
        return f"{0}".encode("iso-8859-1")

    elif num == 2:  # delete existing student
        # student_data = pickle.loads(stud_data)
        string_after_first_dollar = data.split('$')[1:]
        res = Application_Queries.FirebaseQueries.delete_existing_student(obj, string_after_first_dollar)
        print("data=", string_after_first_dollar, " res=", res)
        return f"{res}".encode("iso-8859-1")

    elif num == 3:  # update existing student
        string_after_first_dollar = data.split('$')[1:]
        res = Application_Queries.FirebaseQueries.update_exsiting_student(obj, string_after_first_dollar)
        print("data=", string_after_first_dollar, " res=", res)
        return f"{res}".encode("iso-8859-1")

    elif num == 4:  # print all students
        all_students = Application_Queries.FirebaseQueries.print_all_students(obj)
        all_students = json.dumps(all_students)
        return all_students

    elif num == 5:  # print student
        student_data = data.split('$')[1:]
        student = Application_Queries.FirebaseQueries.print_single_student(obj, student_data)
        if student == -1:
            print("Student dont exist!")
            return "1"
        else:
            print(f'{json.dumps(student)}')
            return f'{json.dumps(student)}'

    elif num == 6:  # print min/max avg of students
        parts = data.split("$")
        avg = int(parts[1])  # 1 - max , 0 - min
        data = Application_Queries.FirebaseQueries.print_avg_student(obj, avg)
        if not data ==-1:
            return_data = ""
            for stud in data:
                return_data += "" + json.dumps(stud)
            return return_data
        else:
            return "1"

    elif num == 7:  # avg of avg
        str = f"{Application_Queries.FirebaseQueries.print_avg_of_avgs(obj)}"
        print(str)
        return str

    elif num == 8:  # factor
        print(data[3:])
        factor = int(data[3:])
        if Application_Queries.FirebaseQueries.factor_students_avg(obj, factor) == -1:
            return f"error occurred!".encode()
        else:
            return f"{factor}"

    elif num == 9:  # condition
        cond = Application_Queries.FirebaseQueries.print_conditon_students(obj)
        if cond == -1:
            return f"error occurred!"
        else:
            data = ""
            for stud in cond:
                print(stud)
                data = data + "$" + json.dumps(stud)
            return data

    elif num == 10: # promote
        ny = Application_Queries.FirebaseQueries.next_year(obj)
        if ny == -1:
            return f"{-1}"
        else:
            return f"{0}"


# Define a function to send ACKs
def send_ack(seq_num, data, num_acks=1):
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
        server_socket.sendto(ack_packet, client_address)
        # Update the received dictionary with the number of ACKs received for the sequence number
        received[seq_num] = num_acks
        # Create TCP socket
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # """
        # Connect to server
        data_sock.connect((SERVER_IP, SERVER_PORT + 1))

        # Send message to server
        return_data = handle_data(data)
        message = f"{return_data}"
        data_sock.send(message.encode())
        # """


# Receive packets
while True:
    # Receive packet
    # print(packets_buffer)
    packet, client_address = server_socket.recvfrom(BUFFER_SIZE)
    packet_data = packet.decode()
    print(packet_data)
    packet_seq_num = int(packet_data.split(':')[0])
    data = packet_data.split(':')[1]
    print(f'Received packet {packet_seq_num}')
    print(f'data: {data}')

    # Add packet to buffer
    packets_buffer[packet_seq_num] = packet

    # Send ACK for received packet
    send_ack(packet_seq_num , data)

    # Update received dictionary
    received[packet_seq_num] = True

    print(
        f'packets_buffer.get(seq_num): {packets_buffer.get(seq_num)} seq_num: {seq_num} window_size: {window_size} len(received) % WINDOW_SIZE: {len(received) % WINDOW_SIZE}')

    # Check if there are packets in the buffer that can be delivered
    while packets_buffer.get(seq_num) and seq_num <= window_size:
        # Deliver packet
        delivered_packet = packets_buffer.pop(seq_num)
        print(f'Delivered packet {seq_num}')
        # Update sequence number
        seq_num += 1

    # Check for out-of-order packets and send cumulative ACKs
    if last_seq + 1 != seq_num - 1:
        # Find the next sequence number that has not been received
        print(f'miss: ')
        missing_seq_num = seq_num
        while missing_seq_num in received:
            missing_seq_num += 1
        # Send a cumulative ACK for all packets up to the missing sequence number
        num_acks = missing_seq_num - window_size
        print(f'seq_num{seq_num} , num_acks {num_acks}')
        send_ack(seq_num, data, num_acks)

    last_seq += 1

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
    # server_socket.settimeout(TIMEOUT)
