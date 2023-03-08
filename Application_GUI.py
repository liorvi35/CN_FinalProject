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


class GUI:
    """

    """

    def __init__(self, master):
        """

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
        """
        TODO - connect to the DHCP server
        """
        pass

    def conn_dns(self):
        """
        TODO - connect to the DNS server
        """
        pass

    def conn_app(self, protocol):
        """
        TODO - connect to the application server - both ways: tcp (protocol = 2), rudp(protocol = 1)
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
                                      command=lambda: self.add_factor_function(protocol), width=20)
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
                                            command=lambda: self.year_up_students_function(protocol), width=20)
        year_up_students_button.config(font=('MS Outlook', 12, 'bold'))
        year_up_students_button.grid(row=3, column=1, padx=20, pady=10)

    def add_student(self, protocol):
        """
        this function is the event when add student button clicked
        :param protocol: protocol number tcp or rudp
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
        this function is validation for input of the event when student was added
        :param data: data of input boxes
        :param frame: add student gui window frame
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
                # TODO - add here RUDP socket that connects to RUDP server that doest the same
                pass
            else:
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

    def delete_student(self, protocol):
        """
        this function is the event when delete student button clicked
        :param protocol: protocol number tcp or rudp
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
        this function is validation for input of the event when student was deleted
        :param data: data of input boxes
        :param frame: add student gui window frame
        :param protocol: tcp or rudp
        """

        res = 1
        if protocol == RUDP:
            # TODO - add here RUDP socket that connects to RUDP server that doest the same
            pass
        else:
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_sock.connect(APP_ADDR)
            tcp_sock.sendall(f"{2}".encode())
            time.sleep(0.0001)
            tcp_sock.sendall(pickle.dumps(data))
            time.sleep(0.0001)
            res = int(tcp_sock.recv(BUFFER_SIZE).decode("iso-8859-1"))
            tcp_sock.shutdown(socket.SHUT_RDWR)
            tcp_sock.close()

        if res == 1:
            messagebox.showerror("Error-Occurred", "ID not found!")
        else:
            messagebox.showinfo("Success", f"Student with ID: {data[2]} was deleted successfully!")
            frame.destroy()

    def update_student(self, protocol):
        """

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

        """

        lengths = [len(string) > 0 for string in data]
        if not all(lengths):
            messagebox.showerror("Error-Occurred", "All data must be filled!")
        else:
            if not (data[1] == "year1" or data[1] == "year2" or data[1] == "year3"):
                messagebox.showerror("Error-Occurred", "Year must be: \'year1\' or \'year2\' or \'year3\' only!")
            elif not data[2].isdigit():
                messagebox.showerror("Error-Occurred", "ID must contain numbers only!")
            elif not (data[3] == "info" or data[3] == "academic"):
                messagebox.showerror("Error-Occurred", "Info/Academic must be: \'info\' or \'academic\' only!")
            elif data[3] == "info":
                if not (data[4] == "email" or data[4] == "firstName" or data[4] == "lastName" or data[4] == "phoneNumber"):
                    messagebox.showerror("Error-Occurred", "Info update-section must be: \'email\' or \'firstName\' or \'lastName\' or \'phoneNumber\' only!")
                elif data[4] == "email" and not (re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", data[5])):
                    messagebox.showerror("Error-Occurred", "E-Mail should have in valid email form!")
                elif data[4] == "phoneNumber" and not data[5].isdigit():
                    messagebox.showerror("Error-Occurred", "Phone-Number must contain numbers only!")
            elif data[3] == "academic":
                if not (data[4] == "avg" or data[4] == "condition" or data[4] == "degree" or data[4] == "track"):
                    messagebox.showerror("Error-Occurred", "Academic update-section must be: \'avg\' or \'condition\' or \'degree\' or \'track\' only!")
                elif data[4] == "avg" and not data[5].isdigit():
                    messagebox.showerror("Error-Occurred", "avg must be a number")
                elif data[4] == "avg" and not (0 <= int(data[5]) <= 100):
                    messagebox.showerror("Error-Occurred", "Average must be a number in range: 0 - 100!")
                elif data[4] == "condition" and not (data[5] == "False" or data[5] == "True"):
                    messagebox.showerror("Error-Occurred", "Condition must be: \'True\' or \'False\' only!")
            res = 1
            if protocol == RUDP:
                # TODO - add here RUDP socket that connects to RUDP server that doest the same
                pass
            else:
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_sock.connect(APP_ADDR)
                tcp_sock.sendall(f"{3}".encode())
                time.sleep(0.001)
                tcp_sock.sendall(pickle.dumps(data))
                time.sleep(0.001)
                res = int(tcp_sock.recv(BUFFER_SIZE).decode("iso-8859-1"))
                tcp_sock.shutdown(socket.SHUT_RDWR)
                tcp_sock.close()

            if res == 1:  # fail
                messagebox.showerror("Error", "ID not found!")
            else:
                messagebox.showinfo("Success", "The operation was successful.")
                frame.destroy()

    def print_all(self, protocol):
        data = ""
        if protocol == RUDP:
            pass
        else:
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_sock.connect(APP_ADDR)
            tcp_sock.sendall(f"{4}".encode())
            time.sleep(0.001)
            data = b""
            while True:
                segment = tcp_sock.recv(1024)
                if not segment:
                    break
                data += segment
            time.sleep(0.01)
            data = json.loads(data)
            tcp_sock.shutdown(socket.SHUT_RDWR)
            tcp_sock.close()

        self.display_table(data)

    def print_specific(self, protocol):
        """

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
                                  command=lambda: self.valid_specific([input_box.get() for input_box in inputs], protocol,
                                                                 frame))
        submit_button.grid(row=11, column=1, pady=10)

    def valid_specific(self, data, protocol, frame):
        # TODO - compleate
        pass

    def print_high_low(self, protocol, avg):
        data = []
        if protocol == 1:
            pass
        else:
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

        self.print_list(data)

    def print_condition(self, protocol):
        data = []
        if protocol == 1:
            pass
        else:
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
            data = pickle.loads(data)

        self.print_list(data)

    def display_table(self, json_data):
        # create the GUI window
        root = tk.Toplevel(self.master)
        root.title("Student Information")

        # create a notebook widget to hold the tables
        notebook = ttk.Notebook(root)

        # iterate through each degree program in the JSON data
        for degree in json_data.keys():
            # create a new frame for each degree program
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=degree)

            # create the table headers
            columns = \
                ("ID", "First Name", "Last Name", "Phone Number", "E-Mail", "Degree", "Track", "Average", "Condition")
            tree = ttk.Treeview(frame, columns=columns, show="headings")

            # set the column widths and alignments
            tree.column("ID", width=50, anchor="center")
            tree.column("First Name", width=100, anchor="w")
            tree.column("Last Name", width=100, anchor="w")
            tree.column("Phone Number", width=100, anchor="w")
            tree.column("E-Mail", width=150, anchor="w")
            tree.column("Degree", width=100, anchor="w")
            tree.column("Track", width=100, anchor="w")
            tree.column("Average", width=50, anchor="center")
            tree.column("Condition", width=50, anchor="center")

            # set the column header text
            for col in columns:
                tree.heading(col, text=col)

            # add the data to the table
            for year in json_data[degree].keys():
                for id_num in json_data[degree][year].keys():
                    student = json_data[degree][year][id_num]
                    tree.insert("", "end", values=(student["info"]["id"],
                                                   student["info"]["firstName"],
                                                   student["info"]["lastName"],
                                                   student["info"]["phoneNumber"],
                                                   student["info"]["email"],
                                                   student["academic"]["degree"],
                                                   student["academic"]["track"],
                                                   student["academic"]["avg"],
                                                   student["academic"]["condition"]))

            # pack the table into the frame
            tree.pack(fill="both", expand=True)

        # pack the notebook into the root window and start the event loop
        notebook.pack(fill="both", expand=True)

    def print_list(self, json_list):
        root = tk.Tk()
        root.title("Student Information")

        # create a treeview with columns
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

        # add data to the treeview
        for i, data in enumerate(json_list):
            student_info = data['info']
            student_academic = data['academic']
            tree.insert('', 'end', values=(
            student_info['id'], student_info['firstName'], student_info['lastName'], student_info['phoneNumber'],
            student_info['email'], student_academic['degree'], student_academic['track'], student_academic['avg'],
            student_academic['condition']))

        # pack and display the treeview
        tree.pack(expand=True, fill='both')
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    my_gui = GUI(root)
    root.mainloop()
