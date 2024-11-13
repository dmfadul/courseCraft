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
        from app.global_vars import ENDING_DATE
        if not self.lectures:
            return 0
        return Lecture.count(self.id, ENDING_DATE, 12)

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
        
        if teacher not in self.teachers:
            self.teachers.append(teacher)
            db.session.commit()
            return f"{teacher.name} added to {self.code}."
        else:
            return f"{teacher.name} is already a part of {self.code}."
        
    def remove_teacher(self, teacher_name):
        from .teacher import Teacher
        teacher = Teacher.query.filter_by(name=teacher_name).first()
        if teacher in self.teachers:
            self.teachers.remove(teacher)
            db.session.commit()
            return f"{teacher.name} removed from {self.code}."
        else:
            return f"{teacher.name} is not a part of {self.code}."
    
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
    