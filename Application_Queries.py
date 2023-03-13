"""
this file contains the queries to the database
Authors: Lior Vinman , Yoad Tamar
Date: 06/03/2023
"""

import json
import firebase_admin
from firebase_admin import db


def get_ids_by_avg(database, avg):
    ids = []
    for dept, years in database.items():
        for year, students in years.items():
            for student_id, info in students.items():
                if info['academic']['avg'] == avg:
                    ids.append(info['info']['id'])
    return ids


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
                obj[k] = int(min(int(obj[k]) + int(x), 100))  # limit to max 100
            else:
                add_to_avgs(v, x)
    elif isinstance(obj, list):
        for i in obj:
            add_to_avgs(i, x)


def get_false_condition_students_ids(obj):
    """
    This function returns a list of ids of all students that have a false condition in the database
    :param obj: json that represent the database
    :return: list of student ids
    """
    student_ids = []
    if isinstance(obj, dict):
        if 'condition' in obj.get('academic', {}):
            if obj['academic']['condition'] == 'True':
                student_ids.append(obj['info']['id'])
        for k, v in obj.items():
            student_ids += get_false_condition_students_ids(v)
    elif isinstance(obj, list):
        for i in obj:
            student_ids += get_false_condition_students_ids(i)
    return student_ids

def get_students_by_ids(json_obj, id_list):
    """
    This function returns the JSON representation of all the students with the ids in the given list
    :param json_obj: JSON object representing the database
    :param id_list: list of student ids to search for
    :return: list of JSON objects representing the matching students
    """
    matching_students = []
    for id in id_list:
        student = get_student_by_id(json_obj, id)
        if student:
            matching_students.append(student)
    return matching_students

def get_student_by_id(json_obj, id):
    """
    This function returns the JSON representation of the student with the given id, if it exists in the given JSON object
    :param json_obj: JSON object representing the database
    :param id: student id to search for
    :return: JSON object representing the matching student, or None if no match is found
    """
    if isinstance(json_obj, dict):
        if 'id' in json_obj.get('info', {}):
            if json_obj['info']['id'] == id:
                return json_obj
        for k, v in json_obj.items():
            student = get_student_by_id(v, id)
            if student:
                return student
    elif isinstance(json_obj, list):
        for i in json_obj:
            student = get_student_by_id(i, id)
            if student:
                return student
    return None


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
                    'avg': int(student_data[8]),
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
            return 1
        else:
            year.child(student_data[2]).delete()
            return 0

    def update_exsiting_student(self, student_data):
        """
        this function update student from the database
        :param: student_data: a list that represent a student: [department , year , id , info/academic , update sub. , update]
        """
        dep = db.reference(student_data[0])
        year = dep.child(student_data[1])
        _id = year.child(student_data[2])
        if _id.get() is None:
            return 1
        else:
            choose = _id.child(student_data[3])
            if student_data[4] == "avg":
                choose.update({student_data[4]:int(student_data[5])})
            else:
                choose.update({student_data[4]:student_data[5]})
            return 0

    def print_all_students(self):
        """
        :return:
        """
        all_stud = db.reference().get()
        return all_stud # change

    def print_single_student(self, student_data):
        """
        this function print all the students from the database
        """
        dep = db.reference(student_data[0])
        year = dep.child(student_data[1])
        student = year.child(student_data[2])
        if student.get() is None:
            return -1
        else:
            return student.get()

    def print_avg_student(self, type):
        """
        this function print the max/min avg
        :param type: if the type equals to 1 - print the max avg , if equals to 0 - the min avg
        """
        data = db.reference().get()
        parsed_data = json.loads(json.dumps(data))
        grades = list(find_grades(parsed_data))
        print(grades)
        if len(grades) > 0:
            grades.sort()
            if int(type) == 1:
                grades.reverse()
                return get_students_by_ids(parsed_data, get_ids_by_avg(parsed_data, grades[0]))
            else:
                print(f"the lowest avg is: {grades[0]}")
                return get_students_by_ids(parsed_data, get_ids_by_avg(parsed_data, grades[0]))
        else:
            print("there is no students")
            return -1

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
            return avg
        else:
            return -1

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
            return 0
        else:
            return -1


    def print_conditon_students(self):
        """
        this function print all the student that have a false condition
        :return:
        """
        data = db.reference().get()
        if data is not None:
            parsed_data = json.loads(json.dumps(data))
            return get_students_by_ids(parsed_data, get_false_condition_students_ids(parsed_data))
        else:
            return -1

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
                for year in sorted(years.keys()):
                    if year == 'year3':  # delete year3
                        del json_obj[department][year]
                    else:  # move students to the next year
                        next_year = 'year' + str(int(year[4:]) + 1)
                        json_obj[department][next_year] = json_obj[department].pop(year)
            db.reference().set(json_obj)
            return 0
        else:
            return -1
