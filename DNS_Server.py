"""
this file is implementation for DNS-SERVER using TCP connection
Authors: Lior Vinman, Yoad Tamar
Date: 27.02.2023
"""

# imports
import socket  # for socket-programming
from datetime import datetime  # for time and data
import validators  # for url-validation
from urllib.parse import urlparse  # for domain extracting

# constants
SERVER_ADDR = ("127.0.0.1", 30763)  # server address and port
BUFFER_SIZE = 2048  # maximal size of received message
NUM_CONN = 300  # maximal number of simultaneously connections


def validate_domain(url):
    """
    this function gets an url (website link) and checks its validation, i.e. checks if it has valid link form
    :param url: an url to check validation
    :return: if valid - url's domain name, else, -1
    """
    if not urlparse(url).scheme:
        url = "http://" + url
    try:
        valid_url = validators.url(url)
    except TypeError:
        return -1
    try:
        if valid_url:
            domain_ip = socket.gethostbyname(urlparse(url).netloc)
        else:
            return -1
    except socket.error:
        return -1
    return domain_ip


def main():
    """
    this is main function, here we're receiving connection from client, then receiving url that he sends,
    checking if its valid url - if yes sending it domain's ip address, if not, sending error message
    :return: -1 - cannot create server's socket
    """
    try:  # every socket operation (socket, bind, listen, accept, recv, sendall) may throw and error

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:  # creating server's socket
            server_sock.bind(SERVER_ADDR)  # binding server's socket
            server_sock.listen(NUM_CONN)  # listening for connections to server's socket
            print(f"listening on: {SERVER_ADDR}")

            while True:
                client_sock, client_addr = server_sock.accept()  # accepting a connection from client
                print(f"[{datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}] got connection from: {client_addr}")

                url = client_sock.recv(BUFFER_SIZE).decode()  # receiving url from client
                print(f"[{datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}] received message from: {client_addr}")
                url = validate_domain(url)  # checking url

                if url == -1:  # if bad url
                    client_sock.sendall("Non-Existent Domain".encode())  # sending error message
                    print(f"[{datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}] sent message to: {client_addr}")
                else:
                    client_sock.sendall(url.encode())  # sending domain's ip
                    print(f"[{datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}] sent message to: {client_addr}")

                client_sock.shutdown(socket.SHUT_RDWR)  # terminating socket
                client_sock.close()  # closing socket

    except socket.error:
        return -1


if __name__ == "__main__":
    main()
