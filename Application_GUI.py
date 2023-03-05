"""
this file is GUI (Graphical User Interface) for project
Authors: Lior Vinman, Yoad Tamar
Date: 05.03.2023
"""

# imports
import socket
import tkinter

# constants
MAIN_WIDTH = 400
MAIN_HEIGHT = 400
DNS_WIDTH = 300
DNS_HEIGHT = 300
DNS_ADDR = ("127.0.0.1", 53)
BUFF_SIZE = 1024

class GUI:
    """
    thiS class is GUI implementation for project
    """

    def main(self):
        """
        this is the main function, is opens the main window with 4 buttons for user:
        1) Connect to DHCP (Dynamic Host Configuration Protocol) Server
        2) Use DNS (Domain Name System)
        3) Use the Student-Management-System via TCP (Transmitted Connection Protocol) protocol
        3) Use the Student-Management-System via RUDP (Reliable User Datagram Protocol) protocol
        """

        main_window = tkinter.Tk()
        main_window.title("Computer Networking - Final Project")
        main_window.geometry(f"{MAIN_WIDTH}x{MAIN_HEIGHT}")

        dhcp_button = tkinter.Button(main_window, text="DHCP", width=10, pady=10)
        dns_button = tkinter.Button(main_window, text="DNS", width=10, pady=10,
                                    command=lambda: self.dns_button_clicked(main_window))
        app_rudp_button = tkinter.Button(main_window, text="APP_RUDP", width=10, pady=10)
        app_tcp_button = tkinter.Button(main_window, text="APP_TCP", width=10, pady=10)

        dhcp_button.pack(side="top", pady=20)
        dns_button.pack(side="top", pady=20)
        app_rudp_button.pack(side="top", pady=20)
        app_tcp_button.pack(side="top", pady=20)

        main_window.configure(bg="#f2f2f2")

        main_window.mainloop()

    def dns_button_clicked(self, root):
        """
        this function is the event when user clicks the DNS button
        here we're opening another window above and asking the user to enter domain name (url)
        """
        dns_window = tkinter.Toplevel(root)
        dns_window.geometry(f"{DNS_WIDTH}x{DNS_HEIGHT}")
        dns_window.title("Domain Name System")

        dns_label = tkinter.Label(dns_window, text="Enter Domain Name:")
        dns_label.pack(pady=(20, 10))
        dns_entry = tkinter.Entry(dns_window, width=30, borderwidth=2, relief="groove")
        dns_entry.pack(pady=10)
        dns_text = tkinter.StringVar()

        dns_label2 = tkinter.Label(dns_window, textvariable=dns_text, justify="center")
        dns_label2.pack(pady=(10, 20))
        dns_button = tkinter.Button(dns_window, text="Print input to console",
                                    command=lambda: dns_text.set(self.conn_dns(dns_entry.get())))
        dns_button.pack(pady=(10, 20))

    def conn_dns(self, url):
        """
        this function sending the data user entered in dns click event to the dns server via UDP socket
        :return: answer the came back from dns (non-existing-domain or the domain's ip)
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(url.encode(), DNS_ADDR)
        
        ans = sock.recv(BUFF_SIZE)
        
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        return ans.decode()


if __name__ == "__main__":
    gui = GUI()
    gui.main()
