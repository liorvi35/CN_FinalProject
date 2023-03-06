"""
this file contains the application server with TCP-connection implementation

Authors: Lior Vinman , Yoad Tamar

Date: 01/03/2023
"""

# imports
import pickle
import socket
import Application_Queries
import firebase_admin
from firebase_admin import credentials
from datetime import datetime  # for time and data


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

        cred = credentials.Certificate("../FireBase_SDK.json")
        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] opened database's credentials")

        firebase_admin.initialize_app(cred, {"databaseURL": "https://cn-finalproject-default-rtdb.firebaseio.com/"})
        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] connected to database")

        obj = Application_Queries.FirebaseQueries()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:

            try:
                server_sock.bind(SERVER_ADDR)
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
                    client_sock.send(f"Student with id = {student_data[1]} was added to database!".encode())

                elif num == "2":  # delete existing student
                    student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                    Application_Queries.FirebaseQueries.delete_existing_student(obj, student_data)
                    client_sock.send(f"Student with id = {student_data[2]} was deleted from database!".encode())

                elif num == "3":  # update existing student
                    student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                    Application_Queries.FirebaseQueries.delete_existing_student(obj, student_data)
                    client_sock.send(f"Student with id = {student_data[2]} was updated!".encode())

                elif num == "4":  # print all students
                    client_sock.send(Application_Queries.FirebaseQueries.print_all_students(obj).encode())

                elif num == "5":  # print student
                    student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                    Application_Queries.FirebaseQueries.delete_existing_student(obj, student_data)
                    client_sock.send(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] "
                                     f"Student with id = {student_data[2]} was deleted from database!".encode())

                elif num == "6":  # print avg of students
                    pass

                elif num == "7":  # avg of avg
                    pass

                elif num == "8":  # factor
                    pass

                elif num == "9":  # condition
                    pass

                client_sock.close()


if __name__ == "__main__":
    ServerTCP.main(__name__)
