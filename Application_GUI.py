"""
this file contains the GUI
Authors: Lior Vinman , Yoad Tamar
Date: 08.03.2023
"""

# imports
import pickle
import socket
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import re

# constants
MAIN_HEIGHT = 370
MAIN_WIDTH = 400
DNS_HEIGHT = 200
DNS_WIDTH = 300
DNS_ADDR = ("127.0.0.1", 53)
BUFFER_SIZE = 1024
APP_HEIGHT = 220
APP_WIDTH = 750
APP_ADDR = ("127.0.0.1", 9090)
TCP = 2
RUDP = 1
SERVER_IP = '127.0.0.1'
RUDP_SERVER_PORT = 1235
DATA_PORT = 1235
WINDOW_SIZE = 4
INITIAL_CWND = 1
THRESHOLD = 8
TIMEOUT = 3
DHCP_SERVER_PORT = 67
DHCP_CLIENT_ADDR = ("0.0.0.0", 9989)
DHCP_DEST = ("<broadcast>", DHCP_SERVER_PORT)

rudp_server_address = (SERVER_IP, RUDP_SERVER_PORT)

# Create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to server address and port
data_sock.bind((SERVER_IP, RUDP_SERVER_PORT + 1))

# Listen for incoming connections
data_sock.listen()

# Initialize variables for sequence numbers, window size, and packets buffer
seq_num = 1
window_size = INITIAL_CWND
packets_buffer = {}


def send_packet(packet):
    global seq_num
    global window_size
    global rudp_server_address
    global client_socket
    client_socket.sendto(packet, rudp_server_address)
    print(f"Sent packet {seq_num}")
    # Add packet to buffer
    packets_buffer[seq_num] = packet

    # Update sequence number and window size
    seq_num += 1
    if seq_num <= window_size:
        window_size = min(window_size * 2, WINDOW_SIZE)
    else:
        window_size += 1 / WINDOW_SIZE

    # Set timeout based on estimated RTT
    start_time = time.time()
    client_socket.settimeout(TIMEOUT)
    while True:
        # Receive ACK
        try:
            ack_packet, _ = client_socket.recvfrom(BUFFER_SIZE)
            end_time = time.time()
            rtt = end_time - start_time
            client_socket.settimeout(max(TIMEOUT - rtt, 0))
        except socket.timeout:
            # Timeout, retransmit unacknowledged packets
            print('Timeout, retransmitting packets')
            window_size = max(window_size / 2, 1)
            for seq, pkt in packets_buffer.items():
                client_socket.sendto(pkt, rudp_server_address)
                print(f'Retransmitted packet {seq}')
            break

        # Parse ACK
        ack_data = ack_packet.decode()
        print(f'ack_data: {ack_data}')
        ack_seq_num = int(ack_data.split(':')[0])
        print(f'Received ACK {ack_seq_num}')

        # Update packets buffer and window size
        if ack_seq_num in packets_buffer:
            del packets_buffer[ack_seq_num]
            if ack_seq_num <= window_size:
                window_size = min(window_size + 1, WINDOW_SIZE)
        else:
            # Duplicate ACK, ignore
            continue

        # Handle out-of-order ACKs
        while len(packets_buffer) > 0:
            if min(packets_buffer.keys()) == ack_seq_num + 1:
                break
            seq = min(packets_buffer.keys())
            pkt = packets_buffer[seq]
            client_socket.sendto(pkt, rudp_server_address)
            print(f'Retransmitted packet {seq}')
            del packets_buffer[seq]

        # Check if all packets have been acknowledged
        if len(packets_buffer) == 0:
            # Accept connection from client
            client_data_socket, client_data_address = data_sock.accept()

            # Receive data from client
            data = b""
            while True:
                segment = client_data_socket.recv(1024)
                if not segment:
                    break
                data += segment
            print(f'Received: {data}')
            return data



def send_data(data):
    global seq_num
    # Divide the message into chunks
    packet = f"{seq_num}:{data}".encode()
    print(packet)
    return send_packet(packet)


class GUI:
    """
    this class is the GUI
    """
    def __init__(self, master):
        """
        GUI's constructor
        :param master: the main GUI window (tk.TK())
        """
        # main window settings
        self.master = master
        master.geometry(f"{MAIN_WIDTH}x{MAIN_HEIGHT}")
        master.title("Computer Networking - Final Project")
        master.config()

        # DHCP button settings
        self.dhcp_button = tk.Button(master, text="Connect to DHCP-Server",
                                     command=self.conn_dhcp, width=20)
        self.dhcp_button.config(font=('MS Outlook', 12, 'bold'))
        self.dhcp_button.pack(padx=20, pady=20)

        # DNS button settings
        self.dns_button = tk.Button(master, text="Use DNS-Server",
                                    command=self.conn_dns, width=20)
        self.dns_button.config(font=('MS Outlook', 12, 'bold'))
        self.dns_button.pack(padx=20, pady=20)

        # APP_RUDP button settings
        self.app_rudp_button = tk.Button(master, text="Application (R-UDP)",
                                         command=lambda: self.conn_app(RUDP), width=20)
        self.app_rudp_button.config(font=('MS Outlook', 12, 'bold'))
        self.app_rudp_button.pack(padx=20, pady=20)

        # APP_TCP button settings
        self.app_tcp_button = tk.Button(master, text="Application (TCP)",
                                        command=lambda: self.conn_app(TCP), width=20)
        self.app_tcp_button.config(font=('MS Outlook', 12, 'bold'))
        self.app_tcp_button.pack(padx=20, pady=20)

        # credits label settings
        self.cred = tk.Label(master, text="Lior Vinman & Yoad Tamar 2023 \u00A9")
        self.cred.config(font=("MS Outlook", 10))
        self.cred.pack()

    def conn_dhcp(self):

        exp_flag = False

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.bind(DHCP_CLIENT_ADDR)
        except (Exception, socket.error) as e:
            messagebox.showerror("Error-Occurred", f"{e}")
            exp_flag = True

        data = self.discover_get()

        try:
            sock.sendto(data, DHCP_DEST)
            data, address = sock.recvfrom(BUFFER_SIZE)
        except (Exception, socket.error) as e:
            messagebox.showerror("Error-Occurred", f"{e}")
            exp_flag = True

        data = self.request_get()

        try:
            sock.sendto(data, DHCP_DEST)
            data, address = sock.recvfrom(BUFFER_SIZE)
        except (Exception, socket.error) as e:
            messagebox.showerror("Error-Occurred", f"{e}")
            exp_flag = True

        if not exp_flag:
            messagebox.showinfo("Success", "DHCP configuration success!")

    def discover_get(self):
        OP = bytes([0x01])
        HTYPE = bytes([0x01])
        HLEN = bytes([0x06])
        HOPS = bytes([0x00])
        XID = bytes([0x39, 0x03, 0xF3, 0x26])
        SECS = bytes([0x00, 0x00])
        FLAGS = bytes([0x00, 0x00])
        CIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        YIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        SIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        GIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR1 = bytes([0x00, 0x05, 0x3C, 0x04])
        CHADDR2 = bytes([0x8D, 0x59, 0x00, 0x00])
        CHADDR3 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR4 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR5 = bytes(192)
        Magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
        DHCPOptions1 = bytes([53, 1, 1])
        DHCPOptions2 = bytes([50, 4, 0xC0, 0xA8, 0x01, 0x64])

        package = OP + HTYPE + HLEN + HOPS + XID + SECS + FLAGS + CIADDR + YIADDR + SIADDR + GIADDR + CHADDR1 + CHADDR2 + CHADDR3 + CHADDR4 + CHADDR5 + Magiccookie + DHCPOptions1 + DHCPOptions2

        return package

    def request_get(self):
        OP = bytes([0x01])
        HTYPE = bytes([0x01])
        HLEN = bytes([0x06])
        HOPS = bytes([0x00])
        XID = bytes([0x39, 0x03, 0xF3, 0x26])
        SECS = bytes([0x00, 0x00])
        FLAGS = bytes([0x00, 0x00])
        CIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        YIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        SIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        GIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR1 = bytes([0x00, 0x0C, 0x29, 0xDD])
        CHADDR2 = bytes([0x5C, 0xA7, 0x00, 0x00])
        CHADDR3 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR4 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR5 = bytes(192)
        Magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
        DHCPOptions1 = bytes([53, 1, 3])
        DHCPOptions2 = bytes([50, 4, 0xC0, 0xA8, 0x01, 0x64])
        DHCPOptions3 = bytes([54, 4, 0xC0, 0xA8, 0x01, 0x01])

        package = OP + HTYPE + HLEN + HOPS + XID + SECS + FLAGS + CIADDR + YIADDR + SIADDR + GIADDR + CHADDR1 + CHADDR2 + CHADDR3 + CHADDR4 + CHADDR5 + Magiccookie + DHCPOptions1 + DHCPOptions2 + DHCPOptions3

        return package

    def conn_dns(self):
        dns_wind = tk.Toplevel(self.master)
        dns_wind.geometry(f"{DNS_WIDTH}x{DNS_HEIGHT}")
        dns_wind.title("Domain Name System")

        dns_label = tk.Label(dns_wind, text="Enter Domain Name:")
        dns_label.config(font=("MS Outlook", 15))
        dns_label.pack(padx=20, pady=10)

        self.dns_box = tk.Entry(dns_wind)
        self.dns_box.pack(padx=20, pady=10)

        self.dns_out = tk.Label(dns_wind, text="")
        self.dns_out.pack(padx=20, pady=10)

        dns_sub = tk.Button(dns_wind, text="Get Domain's IP-Address!", width=20, command=self.dns_submit)
        dns_sub.config(font=("MS Outlook", 10, "bold"))
        dns_sub.pack()

    def dns_submit(self):
        data = self.dns_box.get()

        if data == "":
            messagebox.showerror("Error-Occurred", "Enter non empty url!")
        else:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(DNS_ADDR)
                sock.sendall(data.encode())
                data = sock.recv(BUFFER_SIZE).decode()
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except Exception as e:
                messagebox.showerror("Error-Occurred", "Cannot connect to DNS server!")

        text = data if data == "Non-Existent Domain" else f"Domain's IP Address = {data}"

        self.dns_out.config(text=text)

    def conn_app(self, protocol):
        """
        this function is the application window
        :param protocol: connection protocol - tcp(2) or rudp(1)
        """
        # window settings
        app_tcp_window = tk.Toplevel(self.master)
        app_tcp_window.title(f"Student Management System - {'TCP' if protocol == TCP else 'RUDP'}")
        app_tcp_window.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")

        # (Q1) Add New Student button
        add_student_button = tk.Button(app_tcp_window, text="Add New Student",
                                       command=lambda: self.add_student(protocol), width=20)
        add_student_button.config(font=('MS Outlook', 12, 'bold'))
        add_student_button.grid(row=0, column=0, padx=20, pady=10)

        # (Q2) Delete Existing Student button
        delete_student_button = tk.Button(app_tcp_window, text="Delete Existing Student",
                                          command=lambda: self.delete_student(protocol), width=20)
        delete_student_button.config(font=('MS Outlook', 12, 'bold'))
        delete_student_button.grid(row=0, column=1, padx=20, pady=10)

        # (Q3) Update Existing Student button
        update_student_button = tk.Button(app_tcp_window, text="Update Existing Student",
                                          command=lambda: self.update_student(protocol), width=20)
        update_student_button.config(font=('MS Outlook', 12, 'bold'))
        update_student_button.grid(row=0, column=2, padx=20, pady=10)

        # (4) Get All Students button
        get_all_students_button = tk.Button(app_tcp_window, text="Print All Students",
                                            command=lambda: self.print_all(protocol), width=20)
        get_all_students_button.config(font=('MS Outlook', 12, 'bold'))
        get_all_students_button.grid(row=1, column=0, padx=20, pady=10)

        # (Q5) Get Specific Student button
        get_specific_student_button = tk.Button(app_tcp_window, text="Print Specific Student",
                                                command=lambda: self.print_specific(protocol), width=20)
        get_specific_student_button.config(font=('MS Outlook', 12, 'bold'))
        get_specific_student_button.grid(row=1, column=1, padx=20, pady=10)

        # (Q6) Get Highest Average
        get_outstanding_student_button = tk.Button(app_tcp_window, text="Print Highest Average",
                                                   command=lambda: self.print_high_low(protocol, 1), width=20)
        get_outstanding_student_button.config(font=('MS Outlook', 12, 'bold'))
        get_outstanding_student_button.grid(row=1, column=2, padx=20, pady=10)

        # (Q7) Get Lowest Average
        get_bad_student_button = tk.Button(app_tcp_window, text="Print Lowest Average",
                                           command=lambda: self.print_high_low(protocol, 0), width=20)
        get_bad_student_button.config(font=('MS Outlook', 12, 'bold'))
        get_bad_student_button.grid(row=2, column=0, padx=20, pady=10)

        # (Q8) Add Factor button
        add_factor_button = tk.Button(app_tcp_window, text="Factor Department",
                                      command=lambda: self.factor(protocol), width=20)
        add_factor_button.config(font=('MS Outlook', 12, 'bold'))
        add_factor_button.grid(row=2, column=1, padx=20, pady=10)

        # (Q9) Get Condition Students button
        get_condition_students_button = tk.Button(app_tcp_window, text="Print Condition Students",
                                                  command=lambda: self.print_condition(protocol),
                                                  width=20)
        get_condition_students_button.config(font=('MS Outlook', 12, 'bold'))
        get_condition_students_button.grid(row=2, column=2, padx=20, pady=10)

        # (Q10) Year Up Students button
        year_up_students_button = tk.Button(app_tcp_window, text="Promote Year Department",
                                            command=lambda: self.promote(protocol), width=20)
        year_up_students_button.config(font=('MS Outlook', 12, 'bold'))
        year_up_students_button.grid(row=3, column=1, padx=20, pady=10)

    def add_student(self, protocol):
        """
        this function is the event when add new student button clicked
        :param protocol: tcp or rudp
        """
        frame = tk.Toplevel(self.master)
        frame.title("Add New Student")

        labels = ["Department", "ID", "First Name", "Last Name", "E-Mail", "Phone Number", "Degree", "Track",
                  "Average", "Condition (True/False)"]
        inputs = []

        for i in range(0, 10):
            label = tk.Label(frame, text=f"{labels[i]}:")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="W")
            input_box = tk.Entry(frame)
            input_box.grid(row=i, column=1, padx=10, pady=5, sticky="E")
            inputs.append(input_box)

        submit_button = tk.Button(frame, text="Submit",
                                  command=lambda: self.valid_add([input_box.get() for input_box in inputs], frame,
                                                                 protocol))
        submit_button.grid(row=11, column=1, pady=10)

    def valid_add(self, data, frame, protocol):
        """
        this function is input validation for add new student input
        :param data: data from input boxes
        :param frame: last gui frame
        :param protocol: tcp or rudp
        """
        lengths = [len(string) > 0 for string in data]

        if not all(lengths):
            messagebox.showerror("Error-Occurred", "All data must be filled!")
        elif any(char.isdigit() for char in data[0]):
            messagebox.showerror("Error-Occurred", "Department must contain letters only!")
        elif not data[1].isdigit():
            messagebox.showerror("Error-Occurred", "ID must contain numbers only!")
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", data[4]):
            messagebox.showerror("Error-Occurred", "E-Mail should have in valid email form!")
        elif not data[5].isdigit():
            messagebox.showerror("Error-Occurred", "Phone-Number must contain numbers only!")
        elif (not data[8].isdigit()) or (not (0 <= int(data[8]) <= 100)):
            messagebox.showerror("Error-Occurred", "Average must be a number in range: 0 - 100!")
        elif not (data[9] == "False" or data[9] == "True"):
            messagebox.showerror("Error-Occurred", "Condition must be \'True\' or \'False\' only!")
        else:
            if protocol == RUDP:
                try:
                    pack_string = f"1 ${data[0]}${data[1]}${data[2]}${data[3]}${data[4]}${data[5]}${data[6]}${data[7]}${data[8]}${data[9]}"
                    send_data(pack_string)
                    messagebox.showinfo("Success", f"Student with ID: {data[1]} was added successfully!")
                except Exception as e:
                    print(e)
            else:
                try:
                    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_sock.connect(APP_ADDR)
                    tcp_sock.sendall(f"{1}".encode())
                    time.sleep(0.001)
                    tcp_sock.sendall(pickle.dumps(data))
                    time.sleep(0.001)
                    tcp_sock.shutdown(socket.SHUT_RDWR)
                    tcp_sock.close()
                    messagebox.showinfo("Success", f"Student with ID: {data[1]} was added successfully!")
                    frame.destroy()
                except Exception as e:
                    print(e)

    def delete_student(self, protocol):
        """
        this function is the event when delete student button clicked
        :param protocol: tcp or rudp
        """
        frame = tk.Toplevel(self.master)
        frame.title("Delete Existing Student")

        labels = ["Department", "Year", "ID"]
        inputs = []

        for i in range(0, 3):
            label = tk.Label(frame, text=f"{labels[i]}:")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="W")
            input_box = tk.Entry(frame)
            input_box.grid(row=i, column=1, padx=10, pady=5, sticky="E")
            inputs.append(input_box)

        submit_button = tk.Button(frame, text="Submit",
                                  command=lambda: self.valid_del([input_box.get() for input_box in inputs], protocol,
                                                                 frame))
        submit_button.grid(row=11, column=1, pady=10)

    def valid_del(self, data, protocol, frame):
        """
        this function is input validation for delete student input
        :param data: data from input boxes
        :param frame: last gui frame
        :param protocol: tcp or rudp
        """
        res = 1
        if protocol == RUDP:
            pack_string = f"2 ${data[0]}${data[1]}${data[2]}"
            res = send_data(pack_string)
            my_char = chr(res[2])  # Extract the character '1' from the byte string
            res = int(my_char)  # Convert the character '1' to an integer
        else:
            try:
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_sock.connect(APP_ADDR)
                tcp_sock.sendall(f"{2}".encode())
                time.sleep(0.0001)
                tcp_sock.sendall(pickle.dumps(data))
                time.sleep(0.0001)
                res = int(tcp_sock.recv(BUFFER_SIZE).decode("iso-8859-1"))
                tcp_sock.shutdown(socket.SHUT_RDWR)
                tcp_sock.close()
            except Exception as e:
                print(e)

        if res == 1:
            messagebox.showerror("Error-Occurred", "ID not found!")
        else:
            messagebox.showinfo("Success", f"Student with ID: {data[2]} was deleted successfully!")
            frame.destroy()

    def update_student(self, protocol):
        """
        this function is the event when update student button clicked
        :param protocol: tcp or rudp
        """
        frame = tk.Toplevel(self.master)
        frame.title("Update Existing Student")

        labels = ["Department", "Year", "ID", "Info/Academic", "Update-Section", "New Data"]
        inputs = []

        for i in range(0, 6):
            label = tk.Label(frame, text=f"{labels[i]}:")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="W")
            input_box = tk.Entry(frame)
            input_box.grid(row=i, column=1, padx=10, pady=5, sticky="E")
            inputs.append(input_box)

        submit_button = tk.Button(frame, text="Submit",
                                  command=lambda: self.valid_update([input_box.get() for input_box in inputs], frame,
                                                                 protocol))
        submit_button.grid(row=11, column=1, pady=10)

    def valid_update(self, data, frame, protocol):
        """
        this function is input validation for update student input
        :param data: data from input boxes
        :param frame: last gui frame
        :param protocol: tcp or rudp
        """
        ok = True
        lengths = [len(string) > 0 for string in data]
        if not all(lengths):
            messagebox.showerror("Error-Occurred", "All data must be filled!")
            ok = False
        else:
            if not (data[1] == "year1" or data[1] == "year2" or data[1] == "year3"):
                messagebox.showerror("Error-Occurred", "Year must be: \'year1\' or \'year2\' or \'year3\' only!")
                ok = False
            elif not data[2].isdigit():
                messagebox.showerror("Error-Occurred", "ID must contain numbers only!")
                ok = False
            elif not (data[3] == "info" or data[3] == "academic"):
                messagebox.showerror("Error-Occurred", "info/academic must be: \'info\' or \'academic\' only!")
                ok = False
            elif data[3] == "info":
                if not (data[4] == "email" or data[4] == "firstName" or data[4] == "lastName" or data[4] == "phoneNumber"):
                    messagebox.showerror("Error-Occurred", "Info update-section must be: \'email\' or \'firstName\' or \'lastName\' or \'phoneNumber\' only!")
                    ok = False
                elif data[4] == "email" and not (re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", data[5])):
                    messagebox.showerror("Error-Occurred", "E-Mail should have in valid email form!")
                    ok = False
                elif data[4] == "phoneNumber" and not data[5].isdigit():
                    messagebox.showerror("Error-Occurred", "Phone-Number must contain numbers only!")
                    ok = False
            elif data[3] == "academic":
                if not (data[4] == "avg" or data[4] == "condition" or data[4] == "degree" or data[4] == "track"):
                    messagebox.showerror("Error-Occurred", "Academic update-section must be: \'avg\' or \'condition\' or \'degree\' or \'track\' only!")
                    ok = False
                elif data[4] == "avg" and not data[5].isdigit():
                    messagebox.showerror("Error-Occurred", "avg must be a number")
                    ok = False
                elif data[4] == "avg" and not (0 <= int(data[5]) <= 100):
                    messagebox.showerror("Error-Occurred", "Average must be a number in range: 0 - 100!")
                    ok = False
                elif data[4] == "condition" and not (data[5] == "False" or data[5] == "True"):
                    messagebox.showerror("Error-Occurred", "Condition must be: \'True\' or \'False\' only!")
                    ok = False

            if ok:
                res = 1
                if protocol == RUDP:
                    pack_string = f"3 ${data[0]}${data[1]}${data[2]}${data[3]}${data[4]}${data[5]}"
                    res = send_data(pack_string)
                    my_char = chr(res[2])  # Extract the character '1' from the byte string
                    res = int(my_char)  # Convert the character '1' to an integer
                else:
                    try:
                        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tcp_sock.connect(APP_ADDR)
                        tcp_sock.sendall(f"{3}".encode())
                        time.sleep(0.001)
                        tcp_sock.sendall(pickle.dumps(data))
                        time.sleep(0.001)
                        res = int(tcp_sock.recv(BUFFER_SIZE).decode("iso-8859-1"))
                        tcp_sock.shutdown(socket.SHUT_RDWR)
                        tcp_sock.close()
                    except Exception as e:
                        print(e)

                if res == 1:  # fail
                    messagebox.showerror("Error", "ID not found!")
                else:
                    messagebox.showinfo("Success", "The operation was successful.")
                    frame.destroy()
            else:
                print("wrong input")

    def print_all(self, protocol):
        """
        this function is the event when print all button clicked
        :param protocol: tcp or rudp
        """
        data = {}
        res = 0
        if protocol == RUDP:
            pack_string = f"4 $none"
            data = json.loads(send_data(pack_string))
            if data is None:
                print("data is null")
                res = 1
        else:
            try:
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_sock.connect(APP_ADDR)
                tcp_sock.sendall(f"{4}".encode())
                time.sleep(0.005)
                data = b""
                while True:
                    segment = tcp_sock.recv(1024)
                    if not segment:
                        break
                    data += segment
                time.sleep(0.01)
                tcp_sock.shutdown(socket.SHUT_RDWR)
                tcp_sock.close()
                data = json.loads(data)
                if data is None:
                    res = 1
            except Exception as e:
                print(e)
        if not res == 1:
            self.display_table(data)
        else:
            messagebox.showerror("Error-Occurred", "there is no student in data")


    def print_specific(self, protocol):
        """
        """
        frame = tk.Toplevel(self.master)
        frame.title("print specific Student")

        labels = ["Department", "Year", "ID"]
        inputs = []
        for i in range(0, 3):
            label = tk.Label(frame, text=f"{labels[i]}:")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="W")
            input_box = tk.Entry(frame)
            input_box.grid(row=i, column=1, padx=10, pady=5, sticky="E")
            inputs.append(input_box)

        submit_button = tk.Button(frame, text="Submit",
                                  command=lambda: self.valid_specific([input_box.get() for input_box in inputs], protocol,frame))
        submit_button.grid(row=11, column=1, pady=10)

    def valid_specific(self, data, protocol, frame):
        """

        """
        lengths = [len(string) > 0 for string in data]
        if not all(lengths):
            messagebox.showerror("Error-Occurred", "All data must be filled!")
            ok = False
        elif not (data[1] == "year1" or data[1] == "year2" or data[1] == "year3"):
            messagebox.showerror("Error-Occurred", "Year must be: \'year1\' or \'year2\' or \'year3\' only!")
        elif not data[2].isdigit():
            messagebox.showerror("Error-Occurred", "ID must contain numbers only!")
        else:
            res = 1
            saveData = []
            if protocol == 1:
                pack_string = f"5 ${data[0]}${data[1]}${data[2]}"
                res = send_data(pack_string).decode()
                if res == "1":
                    res = 1
                else:
                    saveData = res
                    res = 2
            else:
                try:
                    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_sock.connect(APP_ADDR)
                    tcp_sock.sendall(f"{5}".encode())
                    time.sleep(0.005)
                    tcp_sock.sendall(pickle.dumps(data))
                    time.sleep(0.001)
                    res = int(tcp_sock.recv(BUFFER_SIZE).decode("iso-8859-1"))
                    if res == 1:
                        messagebox.showerror("Error", "ID not found!")
                    else:
                        saveData = b""
                        while True:
                            segment = tcp_sock.recv(1024)
                            if not segment:
                                break
                            saveData += segment
                    time.sleep(0.01)
                    tcp_sock.shutdown(socket.SHUT_RDWR)
                    tcp_sock.close()
                except Exception as e:
                    print(e)
            if res == 0:
                saveData = json.loads(saveData)
                listd = []
                listd.append(saveData)
                self.print_list(listd)
                frame.destroy()
            elif res == 2:
                listd = []
                listd.append(json.loads(saveData))
                self.print_list(listd)
            else:
                messagebox.showerror("Error-Occurred", "ID not found!")


    def print_high_low(self, protocol, avg):
        """
        this function is the event when print maximum or minimum avg button is clicked
        :param protocol: tcp or rudp
        :param avg: max or min
        """
        data = []
        if protocol == 1:
            pack_string = f"6 ${avg}"
            return_data = send_data(pack_string).decode()
            res = 0
            if not return_data == "1":
                return_data = json.loads(return_data)
                data.append(return_data)
            else:
                res = 1

        else:
            try:
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_sock.connect(APP_ADDR)
                tcp_sock.sendall(f"{6}".encode())
                time.sleep(0.001)
                tcp_sock.sendall(f"{avg}".encode())
                time.sleep(0.001)
                data = b""
                while True:
                    segment = tcp_sock.recv(1024)
                    if not segment:
                        break
                    data += segment
                time.sleep(0.001)
                data = pickle.loads(data)
                tcp_sock.shutdown(socket.SHUT_RDWR)
                tcp_sock.close()
                if data == -1:
                    res = 1
                else:
                    res = 0
            except Exception as e:
                print(e)
        if not res == 1:
            self.print_list(data)
        else:
            messagebox.showerror("Error-Occurred", "there is no student in data")

    def print_condition(self, protocol):
        """
        this function is the event when print condition button is clicked
        :param protocol: tcp or rudp
        """
        data = []
        if protocol == 1:
            pack_string = f"9 $none"
            data = send_data(pack_string).decode()
            data = data.strip('$').split('$')
            res = 1
            if not "error occurred!" in data:
                data_list = []
                for stud in data:
                    data_list.append(stud)
                data.clear()
                for stud in data_list:
                    data.append(json.loads(stud))
                res = 0
        else:
            try:
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_sock.connect(APP_ADDR)
                tcp_sock.sendall(f"{9}".encode())
                time.sleep(0.001)
                data = b""
                while True:
                    segment = tcp_sock.recv(BUFFER_SIZE)
                    if not segment:
                        break
                    data += segment
                time.sleep(0.001)
                res = 1
                if len(data) > 16:
                    data = pickle.loads(data)
                    tcp_sock.shutdown(socket.SHUT_RDWR)
                    tcp_sock.close()
                    res = 0
            except Exception as e:
                print(e)
        if res == 0:
            self.print_list(data)
        else:
            messagebox.showerror("Error-Occurred", "there is no student in data")


    def factor(self, protocol):
        """
        this function is the event when factor button is clicked
        :param protocol: tcp or rudp
        """
        frame = tk.Toplevel(self.master)
        frame.title("Factor")

        label = tk.Label(frame, text="Number of points")
        label.grid(row=0, column=0, padx=10, pady=5, sticky="W")
        input_box = tk.Entry(frame)
        input_box.grid(row=0, column=1, padx=10, pady=5, sticky="E")

        submit_button = tk.Button(frame, text="Submit",
                                  command=lambda: self.factor_valid(input_box.get(), protocol, frame))
        submit_button.grid(row=11, column=1, pady=10)

    def factor_valid(self, data, protocol, frame):
        """
        this function is input validation for factor input
        :param data: data from input boxes
        :param frame: last gui frame
        :param protocol: tcp or rudp
        """

        if not (0 < int(data) <= 100):
            messagebox.showerror("Error-Occurred", "Points must be between 1 - 100 only!")
        else:
            res = -1

            if protocol == RUDP:
                pack_string = f"8 ${data}"
                res = send_data(pack_string)
            else:
                try:
                    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_sock.connect(APP_ADDR)
                    tcp_sock.sendall(f"{8}".encode())
                    time.sleep(0.001)
                    tcp_sock.sendall(f"{data}".encode())
                    time.sleep(0.001)
                    res = int(tcp_sock.recv(BUFFER_SIZE).decode())
                    tcp_sock.shutdown(socket.SHUT_RDWR)
                    tcp_sock.close()
                except Exception as e:
                    print(e)

            if res == "error occurred!":
                messagebox.showerror("Error-Occurred", "Error-Occurred")
            else:
                messagebox.showinfo("Success", f"All students got factor of {data} points!")
                frame.destroy()

    def promote(self, protocol):
        """
        this function is the event when promote year button clicked
        :param protocol: tcp or rudp
        """
        if protocol == RUDP:
            try:
                pack_string = f"10 $none"
                send_data(pack_string)
            except Exception as e:
                print(e)
            messagebox.showinfo("Success", "All student were promoted up a year!")
        else:
            try:
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_sock.connect(APP_ADDR)
                tcp_sock.sendall(f"{10}".encode())
                time.sleep(0.001)
                tcp_sock.shutdown(socket.SHUT_RDWR)
                tcp_sock.close()
            except Exception as e:
                print(e)
            messagebox.showinfo("Success", "All student were promoted up a year!")

    def display_table(self, json_data):
        """
        this function prints all the database in table
        :param json_data: json format of the database
        """
        root = tk.Toplevel(self.master)
        root.title("Student Information")
        notebook = ttk.Notebook(root)

        for degree in json_data.keys():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=degree)

            columns = ("ID", "First Name", "Last Name", "Phone Number", "E-Mail", "Year", "Degree", "Track", "Average",
                       "Condition")
            tree = ttk.Treeview(frame, columns=columns, show="headings")

            tree.column("ID", width=50, anchor="center")
            tree.column("First Name", width=100, anchor="w")
            tree.column("Last Name", width=100, anchor="w")
            tree.column("Phone Number", width=100, anchor="w")
            tree.column("E-Mail", width=150, anchor="w")
            tree.column("Year", width=50, anchor="center")  # New column
            tree.column("Degree", width=100, anchor="w")
            tree.column("Track", width=100, anchor="w")
            tree.column("Average", width=50, anchor="center")
            tree.column("Condition", width=50, anchor="center")

            for col in columns:
                tree.heading(col, text=col)

            for year in json_data[degree].keys():
                for id_num in json_data[degree][year].keys():
                    student = json_data[degree][year][id_num]
                    tree.insert("", "end", values=(student["info"]["id"],
                                                   student["info"]["firstName"],
                                                   student["info"]["lastName"],
                                                   student["info"]["phoneNumber"],
                                                   student["info"]["email"],
                                                   year,  # New value
                                                   student["academic"]["degree"],
                                                   student["academic"]["track"],
                                                   student["academic"]["avg"],
                                                   student["academic"]["condition"]))

            tree.pack(fill="both", expand=True)

        notebook.pack(fill="both", expand=True)

    def print_list(self, json_list):
        """
        this function gets a list of students (by json) and print them in table
        :param json_list: json list of students
        """
        root = tk.Tk()
        root.title("Student Information")

        tree = ttk.Treeview(root, columns=(
        'ID', 'First Name', 'Last Name', 'Phone Number', 'E-Mail', 'Degree', 'Track', 'Average', 'Condition'),
                            show='headings')
        tree.column('ID', width=100)
        tree.column('First Name', width=100)
        tree.column('Last Name', width=100)
        tree.column('Phone Number', width=100)
        tree.column('E-Mail', width=100)
        tree.column('Degree', width=100)
        tree.column('Track', width=100)
        tree.column('Average', width=100)
        tree.column('Condition', width=100)
        tree.heading('ID', text='ID')
        tree.heading('First Name', text='First Name')
        tree.heading('Last Name', text='Last Name')
        tree.heading('Phone Number', text='Phone Number')
        tree.heading('E-Mail', text='E-Mail')
        tree.heading('Degree', text='Degree')
        tree.heading('Track', text='Track')
        tree.heading('Average', text='Average')
        tree.heading('Condition', text='Condition')

        for i, data in enumerate(json_list):
            student_info = data['info']
            student_academic = data['academic']
            tree.insert('', 'end', values=(
            student_info['id'], student_info['firstName'], student_info['lastName'], student_info['phoneNumber'],
            student_info['email'], student_academic['degree'], student_academic['track'], student_academic['avg'],
            student_academic['condition']))

        tree.pack(expand=True, fill='both')
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    my_gui = GUI(root)
    root.mainloop()
