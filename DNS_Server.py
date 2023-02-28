"""
this file is implementation for DNS-SERVER using UDP communication
Authors: Lior Vinman, Yoad Tamar
Date: 28.02.2023
"""

# imports
import socket  # for socket-programming
from datetime import datetime  # for time and data
import validators  # for url-validation
from urllib.parse import urlparse  # for domain extracting

# constants
SERVER_ADDR = ("127.0.0.1", 30763)  # server address and port
BUFFER_SIZE = 2048  # maximal size of received message
ERR = -1  # global err code


class DNS:
    """
    this class is a DNS server implementation
    """

    def get_domain(self, url):
        """
        this function gets an url and checks if it valid
        :param url: the url to check validation
        :return: url's domain if the url valid, -1 else
        """

        if not urlparse(url).scheme:  # checking if url is in legal format
            url = "http://" + url
        try:
            validation = validators.url(url)  # validating url
        except TypeError:
            return ERR
        if validation:
            return urlparse(url).netloc  # returning the domain name
        return ERR


    def main(self):
        """
        this is main function, here we're receiving message from client,
        then checking if its valid url - if yes sending it domain's ip address, if not, sending error message
        :return: -1 - cannot create server's socket
        """

        dns_cache = {}  # dictionary that holding pairs: (domain, ip)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:  # creating UDP socket

            try:
                server_sock.bind(SERVER_ADDR)  # socket binding
            except Exception as e:
                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {e}")

            print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] server bound on: {SERVER_ADDR}")

            while True:

                try:
                    client_msg, client_addr = server_sock.recvfrom(BUFFER_SIZE)  # receiving url
                except Exception as e:
                    print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {e}")

                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] received message from: {client_addr}")

                dom = DNS.get_domain(self, client_msg.decode())  # getting domain name

                if dom == ERR:  # checking if there is an error
                    try:
                        server_sock.sendto("Non-Existent Domain".encode(), client_addr)  # sending error message
                    except Exception as e:
                        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {e}")

                    print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] message has been sent to: {client_addr}")

                    continue

                elif dom not in dns_cache:  # checking if current domain is in cache
                    try:
                        dns_cache[dom] = socket.gethostbyname(dom)
                    except Exception as e:
                        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {e}")

                rep = dns_cache[dom]

                try:
                    server_sock.sendto(rep.encode(), client_addr)  # sending the domain's ip
                except Exception as e:
                    print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {e}")

                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] message has been sent to: {client_addr}")


if __name__ == "__main__":
    DNS.main(__name__)
