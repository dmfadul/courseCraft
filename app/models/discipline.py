from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from .associations import teacher_discipline_association, discipline_prerequisite_association
from app.global_config import ALTERNATING_WEEKS


class Discipline(db.Model):
    __tablename__ = 'disciplines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_abbr = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)
    workload = db.Column(db.Integer, nullable=False)
    is_theoretical = db.Column(db.Boolean, nullable=False)
    is_intensive = db.Column(db.Boolean, nullable=False)
    mandatory_room_id = db.Column(db.Integer, ForeignKey('classrooms.id'), nullable=True)
    joined_cohorts = db.Column(db.Boolean, nullable=False, default=False)
    
    moduli = relationship('Modulus', back_populates='discipline', lazy=True)
    mandatory_room = relationship('Classroom', back_populates='disciplines')

    cohorts = relationship(
        'Cohort', 
        secondary='cohorts_disciplines', 
        back_populates='disciplines'
    )

    teachers = relationship(
        'Teacher', 
        secondary=teacher_discipline_association, 
        back_populates='disciplines'
    )

    prerequisites = relationship(
        'Discipline',
        secondary=discipline_prerequisite_association,
        primaryjoin=code == discipline_prerequisite_association.c.discipline_code,
        secondaryjoin=code == discipline_prerequisite_association.c.prerequisite_code,
        backref='required_for'
    )

    @classmethod
    def add_discipline(cls,
                       name,
                       name_abbr,
                       code,
                       workload,
                       is_theoretical,
                       is_intensive,
                       mandatory_room=None,
                       teachers=None,
                       joined_cohorts=False,):
        teachers = teachers or []

        mandatory_room = mandatory_room or '0'
        existing_codes = [discipline.code for discipline in cls.query.all()]
        if code in existing_codes:
            code = code + 'b'

        new_discipline = cls(name=name,
                             name_abbr=name_abbr,
                             code=code,
                             workload=workload,
                             is_theoretical=is_theoretical,
                             is_intensive=is_intensive,
                             joined_cohorts=joined_cohorts,
                            )
        
        db.session.add(new_discipline)
        new_discipline.add_mandatory_room(mandatory_room)
        
        for teacher in teachers:
            flag = new_discipline.add_teacher(teacher)
            if flag == -1:
                print(f"Teacher {teacher} not found in the database.")
                continue

        db.session.commit()

        if not ALTERNATING_WEEKS and new_discipline.mandatory_room_id == -1:
            new_discipline.add_mandatory_room(0)

        return new_discipline

    def delete_discipline(self):
        for modulus in self.moduli:
            modulus.delete_modulus()

        db.session.delete(self)
        db.session.commit()

    def delete_lectures(self):
        for modulus in self.moduli:
            modulus.delete_lectures()
        return f"Lectures of {self.code} deleted."

    def change_intensive(self):
        self.is_intensive = not self.is_intensive
        db.session.commit()
        return f"Changed intensive status of {self.code} - {self.name} to {'intensive' if self.is_intensive else 'not intensive'}."
    
    def change_theoretical(self):        
        self.is_theoretical = not self.is_theoretical
        if self.is_theoretical and ALTERNATING_WEEKS:
            self.add_mandatory_room(-1)
        else:
            self.add_mandatory_room(0)

        for modulus in self.moduli:
            modulus.remove_main_classroom()
            modulus.set_main_classroom()
        db.session.commit()
        return f"""Changed theoretical status of {self.code} - {self.name} to
        {'theoretical' if self.is_theoretical else 'prática'}.\n
        Mandatory classroom changed to {self.mandatory_room.name}."""
    
    def change_workload(self, new_workload):
        self.workload = new_workload
        db.session.commit()
        return f"Changed workload of {self.code} to {self.workload} hours."

    def add_teacher(self, teacher_name):
        from .teacher import Teacher

        teacher_name = ' '.join([name.capitalize().strip() for name in teacher_name.split(' ')])
        teacher = db.session.query(Teacher).filter_by(name=teacher_name).first()
        if teacher is None:
            return -1

        if teacher not in self.teachers:
            self.teachers.append(teacher)
            db.session.commit()
            return f"{teacher.name} added to {self.code}."
        else:
            return f"{teacher.name} is already a part of {self.code}."

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
    
    def remove_teacher(self, teacher_name):
        from .teacher import Teacher

        teacher = db.session.query(Teacher).filter_by(name=teacher_name).first()
        if teacher in self.teachers:
            self.teachers.remove(teacher)
            db.session.commit()
            return f"{teacher.name} removed from {self.code}."
        else:
            return f"{teacher.name} is not a part of {self.code}."  
    
    def add_prerequisite(self, prerequisite_code):
        """Add a prerequisite discipline by its code."""
        # Find the discipline by code
        prerequisite = db.session.query(Discipline).filter_by(code=prerequisite_code).first()

        if prerequisite is None:
            raise ValueError(f"No discipline found with the code {prerequisite_code}")

        # Add the found discipline to the prerequisites list if it's not already in there
        if prerequisite not in self.prerequisites:
            self.prerequisites.append(prerequisite)
            db.session.commit()
            return f"Prerequisite {prerequisite_code} added to {self.code}."
        else:
            return f"Prerequisite {prerequisite_code} is already a part of {self.code}."
        
    def add_mandatory_room(self, room_code):
        """Add a mandatory room to the discipline."""
        from .classroom import Classroom
        # Find the room by name
        room = db.session.query(Classroom).filter_by(code=room_code).first()

        if room is None:
            raise ValueError(f"No room found with the name {room_code}")

        self.mandatory_room = room
        db.session.commit()
        return f"{room.name} added as mandatory room for {self.code}."

    def change_name(self, new_name, new_abbr):
        self.name = new_name
        self.name_abbr = new_abbr
        db.session.commit()
        return f"Changed name of {self.code} to {self.name}."
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_abbr': self.name_abbr,
            'code': self.code,
            'workload': self.workload,
            'is_theoretical': self.is_theoretical,
            'is_intensive': self.is_intensive,
            'mandatory_room': self.mandatory_room.name if self.mandatory_room else '0',
            'teachers': [teacher.name for teacher in self.teachers],
            'prerequisites': [prerequisite.code for prerequisite in self.prerequisites],
        }