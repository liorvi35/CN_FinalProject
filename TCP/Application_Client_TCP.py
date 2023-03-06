import json
import socket
import time
import pickle

"""
when sending numbers decoding should be in "iso-8859-1" format!!!
"""

SERVER_ADDR = ("127.0.0.1", 9090)
BUFFER_SIZE = 1024



def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(SERVER_ADDR)

    max_min_avg(sock, 0)

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def add_new(sock):
    sock.sendall(f"{1}".encode())
    time.sleep(0.0001)
    param = ["CS", "999", "Yuval", "B", "pljh@gmail.com", "9978456120", "CS",
             "Cyber", 70, "False"]
    data = pickle.dumps(param)
    sock.sendall(data)

def delete_student(sock):
    sock.sendall(f"{2}".encode())
    time.sleep(0.0001)
    param = ["ComputerScience", "year1", "123456789"]
    data = pickle.dumps(param)
    sock.sendall(data)

def update_student(sock):
    sock.sendall(f"{3}".encode())
    time.sleep(0.0001)
    param = ["IndustrialEngineering", "year1", "74125", "info", "phoneNumber", "9725598461"]
    data = pickle.dumps(param)
    sock.sendall(data)

def print_all(sock):
    sock.sendall(f"{4}".encode())
    time.sleep(0.0001)
    data = sock.recv(BUFFER_SIZE).decode()
    print(data)
    data_dict = json.loads(data)
    for subject in data_dict:
        print(f"Table for {subject}:")
        print("ID\tFirst Name\tLast Name\tPhone Number\t\t\tEmail\t\t\tYear\tDegree\tTrack\tAverage\tCondition")
        for year in data_dict[subject]:
            for student_id in data_dict[subject][year]:
                student = data_dict[subject][year][student_id]
                print(
                    f"{student['info']['id']}\t{student['info']['firstName']}\t\t{student['info']['lastName']}"
                    f"\t\t{student['info']['phoneNumber']}\t{student['info']['email']}\t{year}\t{student['academic']['degree']}"
                    f"\t{student['academic']['track']}\t{student['academic']['avg']}\t{student['academic']['condition']}")
        print()

def print_one(sock):
    sock.sendall(f"{5}".encode())
    time.sleep(0.0001)
    param = ["IndustrialEngineering", "year1", "74125"]
    data = pickle.dumps(param)
    sock.sendall(data)
    data = sock.recv(BUFFER_SIZE).decode()
    if data == "Student dont exist!":
        print("err")
    else:
        data = data.replace("'", "\"")
        data_dict = json.loads(data)
        # Print the table header
        print("ID\tFirst Name\tLast Name\tPhone Number\tEmail\t\t\tDegree\t\t\tTrack\t\tAverage\tCondition")

        # Print the student's information as a row in the table
        print(
            f"{data_dict['info']['id']}\t{data_dict['info']['firstName']}\t\t{data_dict['info']['lastName']}\t\t{data_dict['info']['phoneNumber']}\t{data_dict['info']['email']}\t{data_dict['academic']['degree']}\t{data_dict['academic']['track']}\t{data_dict['academic']['avg']}\t{data_dict['academic']['condition']}")

def max_min_avg(sock, t):
    sock.sendall(f"{6}".encode())
    time.sleep(0.0001)
    sock.sendall(f"{t}".encode())
    data = pickle.loads(sock.recv(BUFFER_SIZE))
    # Print table header
    print("ID\tFirst Name\tLast Name\tPhone Number\tEmail\t\t\tDegree\t\t\tTrack\t\tAverage\tCondition")

    # Print data in table
    for d in data:
        print(
            f"{d['info']['id']}\t{d['info']['firstName']}\t\t{d['info']['lastName']}\t\t{d['info']['phoneNumber']}\t{d['info']['email']}\t{d['academic']['degree']}\t{d['academic']['track']}\t{d['academic']['avg']}\t{d['academic']['condition']}")


def avg(sock):
    sock.sendall(f"{7}".encode())
    time.sleep(0.0001)
    print(f"{sock.recv(BUFFER_SIZE).decode('iso-8859-1')}")


def factor(sock, points):
    sock.sendall(f"{8}".encode())
    time.sleep(0.0001)
    sock.sendall(f"{points}".encode())
    print(f"{sock.recv(BUFFER_SIZE).decode()}")

def condition(sock):
    sock.sendall(f"{9}".encode())
    time.sleep(0.0001)
    data = pickle.loads(sock.recv(BUFFER_SIZE))
    # Print table header
    print("ID\tFirst Name\tLast Name\tPhone Number\tEmail\t\t\tDegree\t\t\tTrack\t\tAverage\tCondition")

    # Print data in table
    for d in data:
        print(
            f"{d['info']['id']}\t{d['info']['firstName']}\t\t{d['info']['lastName']}\t\t{d['info']['phoneNumber']}\t{d['info']['email']}\t{d['academic']['degree']}\t{d['academic']['track']}\t{d['academic']['avg']}\t{d['academic']['condition']}")



def next_year(sock):
    sock.sendall(f"{10}".encode())
    time.sleep(0.0001)
    print(f"{sock.recv(BUFFER_SIZE).decode()}")


if __name__ == "__main__":
    main()
