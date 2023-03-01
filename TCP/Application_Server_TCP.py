"""
this file contains the application server with TCP-connection implementation

Authors: Lior Vinman , Yoad Tamar

Date: 01/03/2023
"""
import pickle
# imports
import socket
import Application_Queries
import firebase_admin
from firebase_admin import credentials

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

        firebase_admin.initialize_app(cred, {"databaseURL": "https://cn-finalproject-default-rtdb.firebaseio.com/"})

        obj = Application_Queries.FirebaseQueries()

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_sock.bind(SERVER_ADDR)

        server_sock.listen(NUM_CONN)

        while True:
            client_sock, client_addr = server_sock.accept()

            num = client_sock.recv(BUFFER_SIZE).decode("iso-8859-1")

            if num == "1":  # add new student
                student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                Application_Queries.FirebaseQueries.add_new_student(obj, student_data)
                client_sock.send(f"Student with id = {student_data[1]} was added to database!".encode())

            elif num == "2":  # delete existing student
                student_data = pickle.loads(client_sock.recv(BUFFER_SIZE))
                Application_Queries.FirebaseQueries.delete_existing_student(obj, student_data)
                client_sock.send(f"Student with id = {student_data[2]} was deleted from database!".encode())

            client_sock.close()


if __name__ == "__main__":
    ServerTCP.main(__name__)
