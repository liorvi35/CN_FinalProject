"""

"""

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


class FirebaseQueries:
    """

    """


    def maim(self):
        """

        :return:
        """

        cred = credentials.Certificate("../FireBase_SDK.json")

        firebase_admin.initialize_app(cred, {"databaseURL": "https://cn-finalproject-default-rtdb.firebaseio.com/"})

    def add_new_student(self, student_data):
        """

        :return:
        """



    def delete_existing_student(self, id):
        """

        :return:
        """
        pass

    def update_exsiting_student(self):
        """

        :return:
        """
        pass

    def print_all_students(self):
        """

        :return:
        """
        pass

    def print_single_student(self):
        """

        :return:
        """
        pass

    def print_avg_student(self, type):
        """

        :return:
        """
        pass

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
