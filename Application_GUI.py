"""
this file contains the application GUI (Graphical User Interface)
Authors: Lior Vinman, Yoad Tamar
Date: 07.03.2023
"""

# imports
import pickle
import socket
import time
import tkinter as tk
from tkinter import ttk
import json

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


class GUI:
    """
    this class is the application GUI
    """

    def __init__(self, master):
        """
        this is the GUI constructor, creating the main window
        """
        self.master = master
        master.geometry(f"{MAIN_WIDTH}x{MAIN_HEIGHT}")
        master.title("Computer Networking - Final Project")
        master.config()

        # DHCP button
        self.dhcp_button = tk.Button(master, text="Connect to DHCP-Server", command=self.dhcp_function, width=20)
        self.dhcp_button.config(font=('MS Outlook', 12, 'bold'))
        self.dhcp_button.pack(padx=20, pady=20)

        # DNS button
        self.dns_button = tk.Button(master, text="Use DNS-Server", command=self.dns_function, width=20)
        self.dns_button.config(font=('MS Outlook', 12, 'bold'))
        self.dns_button.pack(padx=20, pady=20)

        # APP_RUDP button
        self.app_rudp_button = tk.Button(master, text="Application (R-UDP)", command=lambda: self.app_function(1), width=20)
        self.app_rudp_button.config(font=('MS Outlook', 12, 'bold'))
        self.app_rudp_button.pack(padx=20, pady=20)

        # APP_TCP button
        self.app_tcp_button = tk.Button(master, text="Application (TCP)", command=lambda: self.app_function(2), width=20)
        self.app_tcp_button.config(font=('MS Outlook', 12, 'bold'))
        self.app_tcp_button.pack(padx=20, pady=20)

        # credits
        self.cred = tk.Label(master, text="Lior Vinman & Yoad Tamar 2023 \u00A9")
        self.cred.config(font=("MS Outlook", 10))
        self.cred.pack()


    def dhcp_function(self):
        """
        TODO - add here DHCP connection and usage (udp ports - 67,68)
        """
        print("DHCP button clicked")

    def dns_function(self):
        """
        this function is the event when DNS button clicked,
        it opens a new window where the user can paste url and get the domain's IP address
        """
        dns_window = tk.Toplevel(self.master)  # open a new window above
        dns_window.geometry(f"{DNS_WIDTH}x{DNS_HEIGHT}")  # set window size
        dns_window.title("Domain Name System")  # set window title

        dns_label = tk.Label(dns_window, text="Enter domain name:")  # text label
        dns_label.config(font=("MS Outlook", 15))
        dns_label.pack(padx=20, pady=10)

        self.dns_entry = tk.Entry(dns_window)  # input box
        self.dns_entry.pack(padx=20, pady=10)
        self.dns_output_label = tk.Label(dns_window, text="")
        self.dns_output_label.pack(padx=20, pady=10)

        # submit button
        dns_submit = tk.Button(dns_window, text="Get Domain's IP-Address!", width=20, command=self.dns_submit_function)
        dns_submit.config(font=('MS Outlook', 10, 'bold'))
        dns_submit.pack()

    def dns_submit_function(self):
        """
        this function is called after the user entered url for getting IP, it opens connection with the DNS Server
        and getting IP (or error message) from him
        """
        data = self.dns_entry.get()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), DNS_ADDR)
        data = sock.recv(BUFFER_SIZE).decode()
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        text = data if data == "Non-Existent Domain" else f"Domain's IP Address = {data}"

        self.dns_output_label.config(text=text)

    def app_function(self, protocol):
        """
        this function is the event when application (both rudp and tcp) button is clicked
        :param protocol: 1 if called by rudp, 2 if called by tcp
        """
        app_tcp_window = tk.Toplevel(self.master)

        title = "TCP" if protocol == 2 else "RUDP"

        app_tcp_window.title(f"Student Management System - {title}")

        app_tcp_window.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")

        # Add New Student button
        add_student_button = tk.Button(app_tcp_window, text="Add New Student",
                                       command=lambda: self.add_student_function(protocol), width=20)
        add_student_button.config(font=('MS Outlook', 12, 'bold'))
        add_student_button.grid(row=0, column=0, padx=20, pady=10)

        # Delete Existing Student button
        delete_student_button = tk.Button(app_tcp_window, text="Delete Existing Student",
                                          command=lambda: self.delete_student_function(protocol), width=20)
        delete_student_button.config(font=('MS Outlook', 12, 'bold'))
        delete_student_button.grid(row=0, column=1, padx=20, pady=10)

        # Update Existing Student button
        update_student_button = tk.Button(app_tcp_window, text="Update Existing Student",
                                          command=lambda: self.update_student_function(protocol), width=20)
        update_student_button.config(font=('MS Outlook', 12, 'bold'))
        update_student_button.grid(row=0, column=2, padx=20, pady=10)

        # Get All Students button
        get_all_students_button = tk.Button(app_tcp_window, text="Print All Students",
                                            command=lambda: self.get_all_students_function(protocol), width=20)
        get_all_students_button.config(font=('MS Outlook', 12, 'bold'))
        get_all_students_button.grid(row=1, column=0, padx=20, pady=10)

        # Get Specific Student button
        get_specific_student_button = tk.Button(app_tcp_window, text="Print Specific Student",
                                                command=lambda: self.get_specific_student_function(protocol), width=20)
        get_specific_student_button.config(font=('MS Outlook', 12, 'bold'))
        get_specific_student_button.grid(row=1, column=1, padx=20, pady=10)

        # Get Outstanding Student button
        get_outstanding_student_button = tk.Button(app_tcp_window, text="Print Highest Average",
                                                   command=lambda: self.get_max_avg(protocol), width=20)
        get_outstanding_student_button.config(font=('MS Outlook', 12, 'bold'))
        get_outstanding_student_button.grid(row=1, column=2, padx=20, pady=10)

        # Get Bad Student button
        get_bad_student_button = tk.Button(app_tcp_window, text="Print Lowest Average",
                                           command=lambda: self.get_min_function(protocol), width=20)
        get_bad_student_button.config(font=('MS Outlook', 12, 'bold'))
        get_bad_student_button.grid(row=2, column=0, padx=20, pady=10)

        # Add Factor button
        add_factor_button = tk.Button(app_tcp_window, text="Factor Department",
                                      command=lambda: self.add_factor_function(protocol), width=20)
        add_factor_button.config(font=('MS Outlook', 12, 'bold'))
        add_factor_button.grid(row=2, column=1, padx=20, pady=10)

        # Get Condition Students button
        get_condition_students_button = tk.Button(app_tcp_window, text="Print Condition Students",
                                                  command=lambda: self.get_condition_students_function(protocol), width=20)
        get_condition_students_button.config(font=('MS Outlook', 12, 'bold'))
        get_condition_students_button.grid(row=2, column=2, padx=20, pady=10)

        # Year Up Students button
        year_up_students_button = tk.Button(app_tcp_window, text="Promote Year Department",
                                            command=lambda: self.year_up_students_function(protocol), width=20)
        year_up_students_button.config(font=('MS Outlook', 12, 'bold'))
        year_up_students_button.grid(row=3, column=1, padx=20, pady=10)

    def add_student_function(self, protocol):
        """
        TODO - add input validation (no input, ...)
        this function is the event when add student button is clicked,
        its opens a window with input boxes to get information
        """
        if protocol == 1:  # rudp
            pass
        else:  # tcp

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

            submit_button = tk.Button(frame, text="Submit", command=lambda: self.valid([input_box.get() for input_box in inputs]))
            submit_button.grid(row=11, column=1, pady=10)

    def valid(self, data):
        print(data)


    def delete_student_function(self, protocol):
        """
        TODO - add input validation (no input, ...)
        this function is the event when delete student button is clicked,
        its opens a window with input boxes to get information
        """
        if protocol == 1:  # rudp
            pass
        else:  # tcp

            frame = tk.Toplevel(self.master)
            frame.title("Add New Student")
            labels = ["Department", "Year", "ID"]
            inputs = []
            for i in range(0, 3):
                label = tk.Label(frame, text=f"{labels[i]}:")
                label.grid(row=i, column=0, padx=10, pady=5, sticky="W")

                input_box = tk.Entry(frame)
                input_box.grid(row=i, column=1, padx=10, pady=5, sticky="E")
                inputs.append(input_box)

            submit_button = tk.Button(frame, text="Submit",
                                      command=lambda: (sock := socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                                                       sock.connect(APP_ADDR),
                                                       sock.sendall(f"{2}".encode()),
                                                       time.sleep(0.0001),
                                                       sock.sendall(
                                                           pickle.dumps([input_box.get() for input_box in inputs])),
                                                       time.sleep(0.0001),
                                                       sock.shutdown(socket.SHUT_RDWR),
                                                       sock.close(),
                                                       frame.destroy()))
            submit_button.grid(row=11, column=1, pady=10)

    def update_student_function(self, protocol):
        """
        TODO - i think its dont working
        this function is the event when update student button is clicked
        """
        if protocol == 1:  # rudp
            pass
        else:  # tcp
            frame = tk.Toplevel(self.master)
            frame.title("Add New Student")
            labels = ["Department", "Year", "ID", "info/academic", "update sub", "update"]
            inputs = []
            for i in range(0, 6):
                label = tk.Label(frame, text=f"{labels[i]}:")
                label.grid(row=i, column=0, padx=10, pady=5, sticky="W")

                input_box = tk.Entry(frame)
                input_box.grid(row=i, column=1, padx=10, pady=5, sticky="E")
                inputs.append(input_box)

            submit_button = tk.Button(frame, text="Submit",
                                      command=lambda: (sock := socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                                                       sock.connect(APP_ADDR),
                                                       sock.sendall(f"{3}".encode()),
                                                       time.sleep(0.0001),
                                                       sock.sendall(
                                                           pickle.dumps([input_box.get() for input_box in inputs])),
                                                       time.sleep(0.0001),
                                                       sock.shutdown(socket.SHUT_RDWR),
                                                       sock.close(),
                                                       frame.destroy()))
            submit_button.grid(row=11, column=1, pady=10)

    def get_all_students_function(self, protocol):
        """
        this function is the event when print all students button is clicked
        """
        if protocol == 1:
            pass
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(APP_ADDR)
            sock.sendall(f"{4}".encode())
            time.sleep(0.0001)
            data = sock.recv(BUFFER_SIZE).decode()
            self.display_tables_from_json(data)

    def get_specific_student_function(self, protocol):
        if protocol == 1:
            pass
        else:
            pass

    def get_max_avg(self, protocol):
        if protocol == 1:
            pass
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(APP_ADDR)
            sock.sendall(f"{6}".encode())
            time.sleep(0.0001)
            sock.sendall(f"{1}".encode())
            time.sleep(0.0001)
            data = pickle.loads(sock.recv(BUFFER_SIZE))
            print(data)
            # self.display_tables_from_json(data)

    def get_min_function(self, protocol):
        print("Get Bad Student button clicked")

    def add_factor_function(self, protocol):
        print("Add Factor button clicked")

    def get_condition_students_function(self, protocol):
        """
        this function is the event when print condition students button is clicked
        """
        if protocol == 1:
            pass
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(APP_ADDR)
            sock.sendall(f"{9}".encode())
            time.sleep(0.0001)
            data = pickle.loads(sock.recv(BUFFER_SIZE))
            self.display_table_from_array(data)

    def year_up_students_function(self, protocol):
        print("Year Up Students button clicked")

    def display_tables_from_json(self, json_str):
        """
        TODO - the next function is print tables from list of Jsons, maybe there is a way to combine these two functions (Or maybe not?)
        TODO - Fix
        this function is to print GUI-Table from Json string, it opens a new window with all tables
        :param json_str: the Json to print tables from it
        """
        data_dict = json.loads(json_str)
        table_window = tk.Toplevel(self.master)
        table_window.title("View Tables")
        for subject in data_dict:
            subject_label = tk.Label(table_window, text=f"Table for {subject}:")
            subject_label.pack()
            table = ttk.Treeview(table_window, columns=(
                "ID", "First Name", "Last Name", "Phone Number", "Email", "Year", "Degree", "Track", "Average",
                "Condition"))
            table.heading("#0", text="ID")
            table.column("#0", width=0, stretch=tk.NO)

            table.heading("#1", text="ID")
            table.column("#1", width=50, stretch=tk.NO)

            table.heading("#2", text="First Name")
            table.column("#2", width=100, stretch=tk.NO)

            table.heading("#3", text="Last Name")
            table.column("#3", width=100, stretch=tk.NO)

            table.heading("#4", text="Phone Number")
            table.column("#4", width=150, stretch=tk.NO)

            table.heading("#5", text="Email")
            table.column("#5", width=200, stretch=tk.NO)

            table.heading("#6", text="Year")
            table.column("#6", width=50, stretch=tk.NO)

            table.heading("#7", text="Degree")
            table.column("#7", width=100, stretch=tk.NO)

            table.heading("#8", text="Track")
            table.column("#8", width=100, stretch=tk.NO)

            table.heading("#9", text="Average")
            table.column("#9", width=100, stretch=tk.NO)

            table.heading("#10", text="Condition")
            table.column("#10", width=100, stretch=tk.NO)

            for year in data_dict[subject]:
                for student_id in data_dict[subject][year]:
                    student = data_dict[subject][year][student_id]
                    table.insert("", tk.END, text=student['info']['id'], values=(
                        student['info']['id'], student['info']['firstName'], student['info']['lastName'],
                        student['info']['phoneNumber'], student['info']['email'], year,
                        student['academic']['degree'], student['academic']['track'],
                        student['academic']['avg'], student['academic']['condition']))
            table.pack()

    def display_table_from_array(self, json_arr):
        """
        this function is to print GUI-Table from list of Jsons, it opens a new window with table
        :param json_arr: the Json to print tables from it
        """
        table_window = tk.Toplevel(self.master)
        table_window.title("Condition Table")

        table = ttk.Treeview(table_window, columns=(
            "ID", "First Name", "Last Name", "Phone Number", "Email", "Degree", "Track", "Average", "Condition"))
        table.heading("#0", text="ID")
        table.column("#0", width=0, stretch=tk.NO)

        table.heading("#0", text="ID")
        table.column("#0", width=100, stretch=tk.NO)

        table.heading("#1", text="First Name")
        table.column("#1", width=100, stretch=tk.NO)

        table.heading("#2", text="Last Name")
        table.column("#2", width=100, stretch=tk.NO)

        table.heading("#3", text="Phone Number")
        table.column("#3", width=150, stretch=tk.NO)

        table.heading("#4", text="Email")
        table.column("#4", width=200, stretch=tk.NO)

        table.heading("#5", text="Degree")
        table.column("#5", width=100, stretch=tk.NO)

        table.heading("#6", text="Track")
        table.column("#6", width=100, stretch=tk.NO)

        table.heading("#7", text="Average")
        table.column("#7", width=100, stretch=tk.NO)

        table.heading("#8", text="Condition")
        table.column("#8", width=100, stretch=tk.NO)

        for student in json_arr:
            table.insert("", tk.END, text=student['info']['id'], values=(
                student['info']['firstName'], student['info']['lastName'],
                student['info']['phoneNumber'], student['info']['email'],
                student['academic']['degree'], student['academic']['track'],
                student['academic']['avg'], student['academic']['condition']))

        table.pack()



if __name__ == "__main__":
    root = tk.Tk()
    my_gui = GUI(root)
    root.mainloop()

