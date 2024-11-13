from app import db
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class Lecture(db.Model):
    __tablename__ = 'lectures'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    grid_position = db.Column(db.Integer, nullable=False)
    modulus_id = db.Column(db.Integer, ForeignKey('moduli.id'), nullable=False)
    classroom_id = db.Column(db.Integer, ForeignKey('classrooms.id'), nullable=True)
    joined_cohorts = db.Column(db.Boolean, nullable=False, default=False)

    modulus = db.relationship('Modulus', back_populates='lectures')
    classroom = db.relationship('Classroom', back_populates='lectures')

    db.UniqueConstraint(date, grid_position, modulus_id)

    @classmethod
    def add_lecture(cls, date, grid_position, class_code, discipline_code, joined=False):
        from .modulus import Modulus
        from .cohort import Cohort
        from .discipline import Discipline
        # from .classroom import Classroom

        cohort_id = Cohort.query.filter_by(code=class_code).first().id
        discipline_id = Discipline.query.filter_by(code=discipline_code).first().id
        modulus = Modulus.query.filter_by(cohort_id=cohort_id, discipline_id=discipline_id).first()
        # classroom_id = Classroom.query.filter_by(code=classroom).first().id

        existing_lectures = cls.query.filter_by(date=date,
                                               grid_position=grid_position,
                                               ).all()
        
        existing_lecture = [l for l in existing_lectures if l.modulus.cohort.id==cohort_id]

        if existing_lecture:
            return -1

        new_lecture = cls(date=date,
                          grid_position=grid_position,
                          modulus=modulus,)

        if new_lecture.modulus.is_complete:
            # print(new_lecture.date, new_lecture.grid_position)
            return 1
        
        joined_cohorts = joined or new_lecture.modulus.joined_cohorts
        new_lecture.joined_cohorts = joined_cohorts

        db.session.add(new_lecture)
        db.session.commit()
        return new_lecture

    def delete_lecture(self):
        db.session.delete(self)
        db.session.commit()

        return 0

    @classmethod
    def count(cls, modulus_id, date, grid_position):
        past_dates = cls.query.filter(cls.modulus_id==modulus_id, cls.date < date).count()
        present_date = cls.query.filter(cls.modulus_id==modulus_id, cls.date == date, cls.grid_position < grid_position).count()
        
        return 1 + past_dates + present_date
    
    @classmethod
    def check_intensive(cls, date):
        lectures = cls.query.filter(cls.date == date).all()
        lectures = [l for l in lectures if l.modulus.discipline.is_intensive]

        return lectures
   
    def set_classroom(self, classroom=None):
        if classroom is not None:
            self.classroom_id = classroom.id
        else:
            self.classroom_id = self.modulus.classroom.id
        
        db.session.commit()
        return self.classroom.name
    
    def change_classroom(self, classroom_name):
        from .classroom import Classroom

        classroom = Classroom.query.filter_by(name=classroom_name).first()
        self.classroom_id = classroom.id
        db.session.commit()
        return self.classroom.name