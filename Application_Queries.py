"""
this file contains the queries to the database

Authors: Lior Vinman , Yoad Tamar

Date: 06/03/2023
"""

import json
import firebase_admin
from firebase_admin import db


def find_grades(obj):
    """
    this function save all the avg of the students in the database
    :param obj: json that represent the database
    :return: return dict that contains all the avg
    """
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
    """
    this function add factor to all avg of the students in the database
    :param obj: json that represent the database
    :param x: the factor to add
    :return: a json that represent the database after the add
    """
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
    """
    this function save all the student that have a false condition in the database
    the function print all the names an ids of those student
    :param obj: json that represent the database
    """
    if isinstance(obj, dict):
        if 'condition' in obj.get('academic', {}):
            if obj['academic']['condition'] == 'False':
                print("id: " + obj['info']['id'], "first name: " + obj['info']['firstName'], "last name: " + obj['info']['lastName'])
        for k, v in obj.items():
            print_false_condition_students(v)
    elif isinstance(obj, list):
        for i in obj:
            print_false_condition_students(i)


class FirebaseQueries:
    """
    this class contians all the queries of the database
    """

    def add_new_student(self, student_data):
        """
        this function add new student to the database
        :param: student_data: a list that represent a student:
                [department, id, first name, last name, email, phone number, degree, track, avg, condition]
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
        this function delete student from the database
        :param: student_data: a list that represent a student: [department, year, id]
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
        this function update student from the database
        :param: student_data: a list that represent a student: [department , year , id , info/academic , update sub. , update]
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
        this function print all the students from the database
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
        this function print the max/min avg
        :param type: if the type equals to 1 - print the max avg , if equals to 0 - the min avg
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
        this function print the avg of all the avg of the students
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
        this function add all the students a factor to avg
        :param x: the factor to add
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
        this function print all the student that have a false condition
        :return:
        """
        data = db.reference().get()
        if data is not None:
            print("the student that have false condition: ")
            parsed_data = json.loads(json.dumps(data))
            print_false_condition_students(parsed_data)
        else:
            print("there is no students")

    def next_year(self):
        """
        this function change every student to his next year 
        if he is on third year - he finishes the degree and delete from the database 
        :return: 
        """
        data = db.reference().get()
        json_obj = json.loads(json.dumps(data))
        if data is not None:
            for department, years in json_obj.items():
                # iterate through each year
                for year in sorted(years.keys()):
                    if year == 'year3':  # delete year3
                        del json_obj[department][year]
                    else:  # move students to the next year
                        next_year = 'year' + str(int(year[4:]) + 1)
                        json_obj[department][next_year] = json_obj[department].pop(year)
            db.reference().set(json_obj)
            print("update!")
        else:
            print("there is no students")


