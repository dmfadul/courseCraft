from app import db
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, object_session
from .associations import teacher_modulus_association
from .lecture import Lecture


class Modulus(db.Model):
    __tablename__ = 'moduli'

    id = db.Column(db.Integer, primary_key=True)
    discipline_id = db.Column(db.Integer, ForeignKey('disciplines.id'), nullable=False)
    cohort_id = db.Column(db.Integer, ForeignKey('cohorts.id'), nullable=False)
    main_classroom_id = db.Column(db.Integer, ForeignKey('classrooms.id'))
    joined_cohorts = db.Column(db.Boolean, nullable=False, default=False)

    teachers = relationship(
        'Teacher',
        secondary=teacher_modulus_association,
        back_populates='moduli',
    )
    
    discipline = relationship('Discipline', back_populates='moduli')
    lectures = relationship('Lecture', back_populates='modulus', lazy=True)
    classroom = relationship('Classroom', back_populates='moduli')

    __table_args__ = (UniqueConstraint('discipline_id', 'cohort_id', name='_discipline_cohort_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.discipline.name,
            'abbrName': self.discipline.name_abbr,
            'disc_code': self.discipline.code,
            'code': self.code,
            'workload': self.discipline.workload,
            'is_theoretical': self.discipline.is_theoretical,
            'is_intensive': self.discipline.is_intensive,
            'classroom': (self.classroom.code, self.classroom.name) if self.classroom else (None, None),
            'teachers': [{'teacher_id': teacher.id, 'teacher_name': teacher.name} for teacher in self.teachers],
            'prerequisites': [prerequisite.code for prerequisite in self.discipline.prerequisites],
        }
    

    @property
    def code(self):
        return f"{self.discipline.code}-{self.cohort.code}"
    
    @property
    def teachers_names(self):
        teachers_names = [teacher.abbr_name for teacher in self.teachers]

        if len(teachers_names) == 0:
            return "Sem professor"
        elif len(teachers_names) == 1:
            return teachers_names[0]
        
        names = [name.split()[0] for name in teachers_names]

        if len(names) == 2:
            return " e ".join(names)
        elif len(names) > 2:
            return ", ".join(names[:-1]) + " e " + names[-1]

        return "Erro desconhecido."
        
    @property
    def start_date(self):
        if not self.lectures:
            return -1
        return self.lectures[0].date

    @property
    def end_date(self):
        if not self.lectures:
            return -1
        return self.lectures[-1].date
    
    @property
    def current_workload(self):
        from app.global_vars import ENDING_DATE, CLASSES_PER_DAY
        if not self.lectures:
            return 0
        return Lecture.count(self.id, ENDING_DATE, CLASSES_PER_DAY)

    @property
    def remaining_workload(self):
        if self.current_workload == 0:
            return self.discipline.workload
        
        return self.discipline.workload - (self.current_workload - 1)

    @property
    def is_complete(self):
        from .lecture import Lecture
        if not self.lectures:
            return False
        lectures = sorted(self.lectures, key=lambda x: (x.date, x.grid_position))
        last_lecture = lectures[-1]

        return Lecture.count(self.id, last_lecture.date, last_lecture.grid_position) >= self.discipline.workload
    
    @property
    def prerequisite_lastdate(self):
        from app.global_vars import STARTING_DATE
        prerequisites = self.discipline.prerequisites
        if not prerequisites:
            return STARTING_DATE
        
        end_dates = []
        for prerequisite in prerequisites:
            modulus = Modulus.query.filter_by(discipline_id=prerequisite.id, cohort_id=self.cohort_id).first()
            end_dates.append(modulus.end_date)

        return max(end_dates)
    
    @classmethod
    def get_by_code(cls, code):
        from .discipline import Discipline
        from .cohort import Cohort

        discipline_code, class_code = code.split('-')
        discipline = Discipline.query.filter_by(code=discipline_code.strip()).first()
        cohort = Cohort.query.filter_by(code=class_code.strip()).first()

        return cls.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()

    @classmethod
    def add_modulus(cls, class_code, discipline_code):
        from .cohort import Cohort
        from .discipline import Discipline

        cohort = Cohort.query.filter_by(code=class_code).first()
        discipline = Discipline.query.filter_by(code=discipline_code).first()

        new_modulus = cls(discipline_id=discipline.id, cohort_id=cohort.id)
        
        db.session.add(new_modulus)
        db.session.commit()
        
        return new_modulus

    def delete_modulus(self):
        for lecture in self.lectures:
            lecture.delete_lecture()
        db.session.delete(self)
        db.session.commit()

    def delete_lectures(self):
        for lecture in self.lectures:
            lecture.delete_lecture()
        db.session.commit()
        return f"Lectures from {self.code} deleted."

    def add_teacher(self, teacher_name):
        from .teacher import Teacher

        teacher = Teacher.query.filter_by(name=teacher_name).first()
        if teacher not in self.discipline.teachers:
            return f"{teacher.name} is not allowed to teach {self.discipline.name}."
        
        if teacher in self.teachers:
            return f"{teacher.name} is already a part of {self.code}."
        
        self.teachers.append(teacher)
        db.session.commit()
        return f"{teacher.name} added to {self.code}."

    def remove_teacher(self, teacher_name):
        from .teacher import Teacher
        teacher = Teacher.query.filter_by(name=teacher_name).first()
        if teacher in self.teachers:
            self.teachers.remove(teacher)
            db.session.commit()
            return f"{teacher.name} removed from {self.code}."
        else:
            return f"{teacher.name} is not a part of {self.code}."
        
    def clear_teachers(self):
        self.teachers = []
        db.session.commit()
        return f"Teachers removed from {self.code}."
    
    def replace_teachers(self, new_teachers):
        for teacher in new_teachers:
            if teacher not in self.discipline.teachers:
                self.discipline.add_teacher(teacher.name)
                print(f"Teacher {teacher.name} added to {self.discipline.code}.")

        self.teachers = new_teachers
        db.session.commit()
        return f"Teachers replaced in {self.code}."

    def set_main_classroom(self, classroom_name=None):
        import random
        from .classroom import Classroom

        if not self.discipline.mandatory_room.code == '0' and classroom_name:
            return f"The discipline {self.discipline.name} has a mandatory classroom {self.discipline.mandatory_room.name}."
        if not self.discipline.mandatory_room.code == '0':
            self.main_classroom_id = self.discipline.mandatory_room.id
        elif classroom_name:
            classroom = Classroom.query.filter_by(name=classroom_name).first()
            self.main_classroom_id = classroom.id
        else:
            classrooms = Classroom.query.filter_by(fungible=True).all()
            self.main_classroom_id = random.choice(classrooms).id

        db.session.commit()
        return f"{self.code} main classroom set to {self.classroom.name}."
        
    def remove_main_classroom(self):
        from .classroom import Classroom

        new_classroom = Classroom.query.filter_by(code=0).first()
        self.classroom_id = new_classroom.id
        self.classroom = new_classroom

        db.session.commit()
        return f"Main classroom removed from {self.code}."
    
    def force_main_classroom(self, classroom_name):
        from .classroom import Classroom

        classroom = Classroom.query.filter_by(name=classroom_name).first()
        if not classroom:
            return f"Classroom {classroom_name} not found."
        
        self.classroom_id = classroom.id
        self.classroom = classroom

        db.session.commit()
        return f"{self.code} main classroom set to {self.classroom.name}."

    def set_joined_cohorts(self):
        self.joined_cohorts = self.discipline.joined_cohorts
        db.session.commit()
        return f"{self.code} now has joined cohorts."
    
    def check_for_teacher_conflict(self, teacher_name):
        from .teacher import Teacher
        teacher = Teacher.query.filter_by(name=teacher_name).first()
        if not teacher:
            return f"Teacher {teacher_name} not found."
        
        for lecture in self.lectures:
            flag = teacher.check_for_conflict(lecture.date, lecture.grid_position, lecture.joined_cohorts)
            if flag:
                return flag
        
        return 0

    def check_for_modulus_conflict(self, discipline_id, cohort_id):
        modulus = Modulus.query.filter_by(discipline_id=discipline_id, cohort_id=cohort_id).first()
        if not modulus:
            return f"Modulus {discipline_id}-{cohort_id} not found."

        if modulus == self:
            return f"Modulus {self.code} is the same as {modulus.code}."

        conflicts = []
        for lecture in self.lectures:
            for other_lecture in modulus.lectures:
                same_date = lecture.date == other_lecture.date
                same_position = lecture.grid_position == other_lecture.grid_position
                if same_date and same_position:
                    if lecture.joined_cohorts and other_lecture.joined_cohorts:
                        if lecture.classroom_id == other_lecture.classroom_id:
                            continue
                    conflicts.append((lecture, other_lecture))

        return conflicts