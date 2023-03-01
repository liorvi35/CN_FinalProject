import socket
import time
import pickle


SERVER_ADDR = ("127.0.0.1", 9090)
BUFFER_SIZE = 1024

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(SERVER_ADDR)

    sock.sendall("1".encode())

    time.sleep(0.0000001)

    list = ["CS", "1", "a", "b", "@gmail.com", "055902002", "CS", "Cyber", 50, "True"]

    # list = ["ComputerScience", "year1", "T6"]

    data = pickle.dumps(list)

    sock.sendall(data)


    print(sock.recv(BUFFER_SIZE).decode())

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
