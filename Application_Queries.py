'''

'''

import firebase_admin
import os

from firebase_admin import credentials
from firebase_admin import db


class FirebaseQueries:
    """

    """

    def maim(self):
        """

        :return:
        """

        cred = credentials.Certificate("FireBase_SDK.json")

        firebase_admin.initialize_app(cred, {"databaseURL": "https://cn-finalproject-default-rtdb.firebaseio.com/"})

    def add_new_student(self, student_data):
        """

        :return:
        """
        depart = open("depart.txt", "a")
        depart.close()

        depart = open("depart.txt", "r")
        contain = False
        for x in depart:
            if x == student_data[0]:
                contain = True
        depart.close()

        depart = open("depart.txt", "a")
        if not contain:
            depart.write(student_data[0] + '\n')

        depart.close()

        f = open(student_data[0] + ".txt", "a")
        f.write(student_data[1] + "\n")
        f.close()
        dep = db.reference(student_data[0])
        year = dep.child('year1')
        year.update({
            student_data[1]: {
                'info': {
                    'id': student_data[1],
                    'firstName': student_data[2],
                    'lastName': student_data[3],
                    'email': student_data[4],
                    'phoneNumber': student_data[5]
                },
                'academic': {
                    'degree': student_data[6],
                    'track': student_data[7],
                    'avg': student_data[8],
                    'condition': student_data[9]
                }
            }
        })

    def delete_existing_student(self, student_data):
        """

        :return:
        """
        delete = open(student_data[0] + "edit.txt", "a")
        f = open(student_data[0] + ".txt", "r")
        for line in f:
            if line != student_data[2]:
                delete.write(line + "\n")

        f.close()
        f = open(student_data[0] + ".txt", "w")
        f.write("")
        f.close()
        f = open(student_data[0] + ".txt", "a")
        for line in delete:
            delete.write(line + "\n")

        delete.close()
        f.close()
        if os.path.exists(student_data[0] + "edit.txt"):
            os.remove(student_data[0] + "edit.txt")

        dep = db.reference(student_data[0])
        year = dep.child(student_data[1])
        year.child(student_data[2]).delete()

    def update_exsiting_student(self):
        """

        :return:
        """
        pass

    def print_all_students(self):
        """

        :return:
        """
        all_stud = db.reference().get()
        print(all_stud)

    def print_single_student(self, student_data):
        """

        :return:
        """
        dep = db.reference(student_data[0])
        year = dep.child(student_data[1])
        print(year.child(student_data[2]).get())

    def print_avg_student(self, type):
        """

        :return:
        """

    def print_avg_of_avgs(self):
        """

        :return:
        """
        pass

    def factor_students_avg(self):
        """

        :return:
        """
        pass

    def print_conditon_students(self):
        """

        :return:
        """
        pass


if __name__ == "__main__":
    cred_obj = firebase_admin.credentials.Certificate('FireBase_SDK.json')
    default_app = firebase_admin.initialize_app(cred_obj, {
        'databaseURL': 'https://cn-finalproject-default-rtdb.firebaseio.com'
    })
    firebase = FirebaseQueries
    FirebaseQueries.print_avg_student(firebase, 1)
