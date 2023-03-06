'''

'''
import json

import firebase_admin
import os

from firebase_admin import credentials
from firebase_admin import db


def find_ids(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'id':
                yield v
            else:
                yield from find_ids(v)
    elif isinstance(obj, list):
        for i in obj:
            yield from find_ids(i)


def find_grades(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'avg':
                yield v
            else:
                yield from find_grades(v)
    elif isinstance(obj, list):
        for i in obj:
            yield from find_grades(i)


def add_to_avgs(obj, x):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'avg':
                obj[k] = min(obj[k] + x, 100)  # limit to max 100
            else:
                add_to_avgs(v, x)
    elif isinstance(obj, list):
        for i in obj:
            add_to_avgs(i, x)


def print_false_condition_students(obj):
    if isinstance(obj, dict):
        if 'condition' in obj.get('academic', {}):
            if obj['academic']['condition'] == 'False':
                print("id: " + obj['info']['id'], "first name: " +  obj['info']['firstName'], "last name: " + obj['info']['lastName'])
        for k, v in obj.items():
            print_false_condition_students(v)
    elif isinstance(obj, list):
        for i in obj:
            print_false_condition_students(i)







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
        dep = db.reference(student_data[0])
        year = dep.child(student_data[1])
        student = year.child(student_data[2])
        if student.get() is None:
            print(f'Student with ID {student_data[2]} does not exist.')
        else:
            year.child(student_data[2]).delete()
            print(f'Student with ID {student_data[2]} deleted.')

    def update_exsiting_student(self, student_data):
        """
        [department , year , id , info/academic , update sub. , update to]
        :return:
        """
        dep = db.reference(student_data[0])
        year = dep.child(student_data[1])
        _id = year.child(student_data[2])
        if _id.get() is None:
            print(f'Student with ID {student_data[2]} does not exist.')
        else:
            choose = _id.child(student_data[3])
            choose.update({student_data[4]:student_data[5]})
            print(f'Student with ID {student_data[2]} updated.')


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
        student = year.child(student_data[2])
        if student.get() is None:
            print(f'Student with ID {student_data[2]} does not exist.')
        else:
            print(student.get())

    def print_avg_student(self, type):
        """
        if the type equals to 1 - print the max avg , if equals to 0 - the min avg
        :return:
        """
        data = db.reference().get()
        parsed_data = json.loads(json.dumps(data))
        grades = list(find_grades(parsed_data))
        if len(grades) > 0:
            grades.sort()
            if type == 1:
                grades.reverse()
                print(f"the highest avg is: {grades[0]}")
            else:
                print(f"the lowest avg is: {grades[0]}")
        else:
            print("there is no students")

    def print_avg_of_avgs(self):
        """

        :return:
        """
        data = db.reference().get()
        parsed_data = json.loads(json.dumps(data))
        grades = list(find_grades(parsed_data))
        if len(grades) > 0:
            avg = sum(grades)
            avg = avg / len(grades)
            print(f"the avg is: {avg}")
        else:
            print("there is no students")

    def factor_students_avg(self, x):
        """

        :return:
        """
        data = db.reference().get()
        parsed_data = json.loads(json.dumps(data))
        if data is not None:
            add_to_avgs(parsed_data, x)
            db.reference().set(parsed_data)
            print(f"all the student get factor of {x} to their avg")
        else:
            print("there is no students")


    def print_conditon_students(self):
        """

        :return:
        """
        data = db.reference().get()
        if data is not None:
            print("the student that have false condition: ")
            parsed_data = json.loads(json.dumps(data))
            print_false_condition_students(parsed_data)
        else:
            print("there is no students")


if __name__ == "__main__":
    cred_obj = firebase_admin.credentials.Certificate('FireBase_SDK.json')
    default_app = firebase_admin.initialize_app(cred_obj, {
        'databaseURL': 'https://cn-finalproject-default-rtdb.firebaseio.com'
    })
    firebase = FirebaseQueries()
    #         [department , year , id , info/academic , update sub. , update to]
    FirebaseQueries.update_exsiting_student(firebase , ["CS" , "year1" , "123" , "academic", "avg" , "1331310"])
