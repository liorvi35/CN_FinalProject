"""
this file contains the application server with TCP-connection implementation

Authors: Lior Vinman , Yoad Tamar

Date: 01/03/2023
"""
import json
# imports
import pickle
import socket

from future.backports.datetime import time

import Application_Queries
import firebase_admin
from firebase_admin import credentials
from datetime import datetime  # for time and data
import time


# constants
SERVER_ADDR = ("127.0.0.1", 9090)
NUM_CONN = 300
BUFFER_SIZE = 1024


class ServerTCP:
    """
    this class is implementation for the app server with TCP communication
    """

    def main(self):
        """

        :return:
        """

        cred = credentials.Certificate("FireBase_SDK.json")
        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] opened database's credentials")

        firebase_admin.initialize_app(cred, {"databaseURL": "https://cn-finalproject-default-rtdb.firebaseio.com/"})
        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] connected to database")

        obj = Application_Queries.FirebaseQueries()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:

            try:
                server_sock.bind(SERVER_ADDR)
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except Exception as e:
                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {e}")

            print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] server bound on: {SERVER_ADDR}")

            try:
                server_sock.listen(NUM_CONN)
            except Exception as e:
                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {e}")

            print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] listening for incoming connections")

            while True:
                try:
                    client_sock, client_addr = server_sock.accept()
                except Exception as e:
                    print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {e}")

                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] got connection from: {client_addr}")

                num = client_sock.recv(BUFFER_SIZE).decode("iso-8859-1")

                print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] received message from: {client_addr}")

                if num == "1":  # add new student
                    student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                    Application_Queries.FirebaseQueries.add_new_student(obj, student_data)
                    client_sock.sendall(f"Student with id = {student_data[1]} was added to database!".encode())

                elif num == "2":  # delete existing student
                    student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                    res = Application_Queries.FirebaseQueries.delete_existing_student(obj, student_data)
                    client_sock.sendall(f"{res}".encode())
                    print("data=", student_data, " res=", res)

                elif num == "3":  # update existing student
                    student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                    res = Application_Queries.FirebaseQueries.update_exsiting_student(obj, student_data)
                    client_sock.sendall(f"{res}".encode())

                elif num == "4":  # print all students
                    all_students = Application_Queries.FirebaseQueries.print_all_students(obj)
                    all_students = json.dumps(all_students)
                    client_sock.sendall(all_students.encode())

                elif num == "5":  # print student
                    student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                    student = Application_Queries.FirebaseQueries.print_single_student(obj, student_data)
                    if student == -1:
                        print("Student dont exist!")
                        client_sock.sendall(f"{1}".encode())
                    else:
                        client_sock.sendall(f"{0}".encode())
                        time.sleep(0.0001)
                        student = json.dumps(student)
                        client_sock.sendall(student.encode())

                elif num == "6":  # print min/max avg of students
                    avg = client_sock.recv(BUFFER_SIZE).decode("iso-8859-1")  # 1 - max , 0 - min
                    data = Application_Queries.FirebaseQueries.print_avg_student(obj, avg)
                    print("data=", data)
                    data = pickle.dumps(data)
                    client_sock.sendall(data)

                elif num == "7":  # avg of avg
                    client_sock.sendall(f"{Application_Queries.FirebaseQueries.print_avg_of_avgs(obj)}".encode())

                elif num == "8":  # factor
                    factor = client_sock.recv(BUFFER_SIZE).decode("iso-8859-1")
                    factor = int(factor)
                    if Application_Queries.FirebaseQueries.factor_students_avg(obj, factor) == -1:
                        client_sock.sendall(f"error occurred!".encode())
                    else:
                        client_sock.sendall(f"{factor} ".encode())

                elif num == "9":  # condition
                    cond = Application_Queries.FirebaseQueries.print_conditon_students(obj)
                    if cond == -1:
                        client_sock.sendall(f"error occurred!".encode())
                    else:
                        data = pickle.dumps(cond)
                        client_sock.sendall(data)

                elif num == "10":
                    ny = Application_Queries.FirebaseQueries.next_year(obj)
                    if ny == -1:
                        client_sock.sendall(f"{-1}".encode())
                    else:
                        client_sock.sendall(f"{0}".encode())

                client_sock.close()


if __name__ == "__main__":
    ServerTCP.main(__name__)
