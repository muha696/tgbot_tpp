import sqlite3





class DBbot:

    def __init__(self, dbfile):
        self.con = sqlite3.connect(dbfile, check_same_thread=False)
        self.cur = self.con.cursor()


    def add_user(self, user_id):
        with self.con:
            result = self.cur.execute(
                f"""INSERT INTO users (user_id) VALUES ('{user_id}')""")
        return result

    def user_check(self, user_id):
        with self.con:
            result = self.cur.execute(f"""SELECT * FROM users WHERE user_id = '{user_id}'""").fetchall()
        return bool(len(result))

    def reg_tutor_admin(self, surname, name, patronomic, check_code):
        with self.con:
            result = self.cur.execute(f"""INSERT INTO tutors (surname, name, patronomic, check_code) VALUES ('{surname}','{name}', '{patronomic}', '{check_code}')""")
        return result

    def reg_tutor_end(self, check_code, user_id, chat_id):
        with self.con:
            result = self.cur.execute(f"""UPDATE tutors SET user_id ='{user_id}', chat_id = '{chat_id}' WHERE check_code = '{check_code}'""")

    def check_code(self, check_code):
        with self.con:
            result = self.cur.execute(f"""SELECT * FROM tutors WHERE check_code = '{check_code}'""").fetchall()
        return bool(len(result))

    def register_student(self, surname, group, user_id, chat_id):
        with self.con:
            result = self.cur.execute(
                f"""INSERT INTO students (surname, group_study, user_id, chat_id) VALUES ('{surname}','{group}', '{user_id}', '{chat_id}')""")
        return result

    def add_discipline(self, discipline_name, group, tutor, attestation):
        with self.con:
            result = self.cur.execute(
                f"""INSERT INTO disciplines (discipline_name, group_study, tutor, attestation) VALUES ('{discipline_name}','{group}', '{tutor}', '{attestation}')""")
        return result

    def check_tutor(self, user_id):
        with self.con:
            result = self.cur.execute(f"""SELECT * FROM tutors WHERE user_id = '{user_id}'""").fetchall()
        return bool(len(result))

    def check_student(self, user_id):
        with self.con:
            result = self.cur.execute(f"""SELECT * FROM students WHERE user_id = '{user_id}'""").fetchall()
        return bool(len(result))

    def check_disp_student(self, study_group):
        with self.con:
            result = self.cur.execute(f"""SELECT * FROM disciplines WHERE group_study = '{study_group}'""").fetchall()
        return bool(len(result))

    def add_to_check(self, student_id, discipline_id, student_group, tutor_id, on_check = False, rework = False, admittance = False, passed = False):
        with self.con:
            result = self.cur.execute(f"""INSERT INTO check_att (student_id, discipline_id, student_group, tutor_id, on_check, rework, admittance, passed) VALUES 
            ('{student_id}', '{discipline_id}', '{student_group}', '{tutor_id}', '{on_check}', '{rework}', '{admittance}', '{passed}')""")
        return result

    def update_to_check(self, check_id, check):
        with self.con:
            if check == 'on_check':
                result = self.cur.execute(
                    f"""UPDATE check_att SET on_check ='True', rework = 'False', admittance = 'False',passed = 'False' WHERE id = '{check_id}'""")
            elif check == 'rework':
                result = self.cur.execute(
                    f"""UPDATE check_att SET on_check ='False', rework = 'True', admittance = 'False',passed = 'False' WHERE id = '{check_id}'""")
            elif check == 'admwork':
                result = self.cur.execute(
                    f"""UPDATE check_att SET on_check ='False', rework = 'False', admittance = 'True',passed = 'False' WHERE id = '{check_id}'""")
            elif check == 'passed':
                result = self.cur.execute(
                    f"""UPDATE check_att SET on_check ='False', rework = 'False', admittance = 'False',passed = 'True' WHERE id = '{check_id}'""")
            else:
                pass
        return result

    def check_get_disp_to_check(self, student_id, disp_id):
        with self.con:
            result = self.cur.execute(f"""SELECT * FROM check_att WHERE student_id = '{student_id}' AND discipline_id = '{disp_id}'""").fetchall()
        return bool(len(result))



    def select_info(self, data, table, column, value):
        with self.con:
            if data == '*':
                result = self.cur.execute(f"""SELECT * FROM {table} WHERE {column} = '{value}'""").fetchall()
            else:
                result = self.cur.execute(f"""SELECT {data} FROM {table} WHERE {column} = '{value}'""").fetchall()
        return result

    def close(self):
        self.con.close()

