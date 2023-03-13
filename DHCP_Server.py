"""
this file contains the DHCP server
Authors: Lior Vinman & Yoad Tamar
Date: 12.03.2023
"""

# imports
import socket
from datetime import datetime

# constants
BUFFER_SIZE = 1024
DHCP_DEST = ('255.255.255.255', 9989)
ADDR = ('', 67)


class DHCP(object):
    """
    this class is the DHCP server
    """

    def main(self):
        """
        this function is the main function that runs the server
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] socket is created!")

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]  socket options set!")

        sock.bind(ADDR)

        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]  socket bound on: {ADDR}")

        while True:
            try:
                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] waiting for DHCP discovery...")
                data, address = sock.recvfrom(BUFFER_SIZE)
                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] received DHCP discovery!")

                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] DHCP offer has been sent!")
                data = self.offer_get()
                sock.sendto(data, DHCP_DEST)
                while True:
                    try:
                        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] waiting for DHCP request")

                        data, address = sock.recvfrom(BUFFER_SIZE)
                        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] received DHCP request!")

                        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] sent DHCP packet")
                        data = self.pack_get()
                        sock.sendto(data, DHCP_DEST)
                        break
                    except (Exception, socket.error) as e:
                        raise e
            except (Exception, socket.error) as e:
                raise e

    def offer_get(self):
        """
        This function creates a DHCP offer package to send to a DHCP client.
        :returns: package (bytes): a byte string representing the DHCP offer package to be sent to the client
        """
        OP = bytes([0x02])
        HTYPE = bytes([0x01])
        HLEN = bytes([0x06])
        HOPS = bytes([0x00])
        XID = bytes([0x39, 0x03, 0xF3, 0x26])
        SECS = bytes([0x00, 0x00])
        FLAGS = bytes([0x00, 0x00])
        CIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        YIADDR = bytes([0xC0, 0xA8, 0x01, 0x64])  # 192.168.1.100
        SIADDR = bytes([0xC0, 0xA8, 0x01, 0x01])  # 192.168.1.1
        GIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR1 = bytes([0x00, 0x05, 0x3C, 0x04])
        CHADDR2 = bytes([0x8D, 0x59, 0x00, 0x00])
        CHADDR3 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR4 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR5 = bytes(192)
        Magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
        DHCPOptions1 = bytes([53, 1, 2])  # DHCP Offer
        DHCPOptions2 = bytes([1, 4, 0xFF, 0xFF, 0xFF, 0x00])  # 255.255.255.0 subnet mask
        DHCPOptions3 = bytes([3, 4, 0xC0, 0xA8, 0x01, 0x01])  # 192.168.1.1 router
        DHCPOptions4 = bytes([51, 4, 0x00, 0x01, 0x51, 0x80])  # 86400s(1 day) IP address lease time
        DHCPOptions5 = bytes([54, 4, 0xC0, 0xA8, 0x01, 0x01])  # DHCP server

        package = OP + HTYPE + HLEN + HOPS + XID + SECS + FLAGS + CIADDR + YIADDR + SIADDR + GIADDR + CHADDR1 + CHADDR2 + CHADDR3 + CHADDR4 + CHADDR5 + Magiccookie + DHCPOptions1 + DHCPOptions2 + DHCPOptions3 + DHCPOptions4 + DHCPOptions5

        return package

    def pack_get(self):
        """
        Generates a DHCP request packet.
        :returns: bytes: A byte string representing the DHCP request packet.
        """
        OP = bytes([0x02])
        HTYPE = bytes([0x01])
        HLEN = bytes([0x06])
        HOPS = bytes([0x00])
        XID = bytes([0x39, 0x03, 0xF3, 0x26])
        SECS = bytes([0x00, 0x00])
        FLAGS = bytes([0x00, 0x00])
        CIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        YIADDR = bytes([0xC0, 0xA8, 0x01, 0x64])
        SIADDR = bytes([0xC0, 0xA8, 0x01, 0x01])
        GIADDR = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR1 = bytes([0x00, 0x05, 0x3C, 0x04])
        CHADDR2 = bytes([0x8D, 0x59, 0x00, 0x00])
        CHADDR3 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR4 = bytes([0x00, 0x00, 0x00, 0x00])
        CHADDR5 = bytes(192)
        Magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
        DHCPOptions1 = bytes([53, 1, 5])  # DHCP ACK(value = 5)
        DHCPOptions2 = bytes([1, 4, 0xFF, 0xFF, 0xFF, 0x00])  # 255.255.255.0 subnet mask
        DHCPOptions3 = bytes([3, 4, 0xC0, 0xA8, 0x01, 0x01])  # 192.168.1.1 router
        DHCPOptions4 = bytes([51, 4, 0x00, 0x01, 0x51, 0x80])  # 86400s(1 day) IP address lease time
        DHCPOptions5 = bytes([54, 4, 0xC0, 0xA8, 0x01, 0x01])  # DHCP server

        package = OP + HTYPE + HLEN + HOPS + XID + SECS + FLAGS + CIADDR + YIADDR + SIADDR + GIADDR + CHADDR1 + CHADDR2 + CHADDR3 + CHADDR4 + CHADDR5 + Magiccookie + DHCPOptions1 + DHCPOptions2 + DHCPOptions3 + DHCPOptions4 + DHCPOptions5

        return package


if __name__ == "__main__":
    dhcp_server = DHCP()
    dhcp_server.main()
