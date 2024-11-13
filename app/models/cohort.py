from app import db
from sqlalchemy.orm import relationship


class Cohort(db.Model):
    __tablename__ = 'cohorts'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False, unique=True)
    number_of_students = db.Column(db.Integer, nullable=False)
    lunch_position = db.Column(db.Integer, nullable=False)
    theoretical_week_parity = db.Column(db.Integer, nullable=False)

    moduli = relationship('Modulus', backref='cohort', lazy=True)

    disciplines = relationship(
        'Discipline',
        secondary='cohorts_disciplines',
        back_populates='cohorts'
    )
    
    @classmethod
    def add_cohort(cls, cohort_code, number_of_students, lunch_position, theoretical_week_parity):
        new_cohort = cls(code=cohort_code,
                         number_of_students=number_of_students,
                         lunch_position=lunch_position,
                         theoretical_week_parity=theoretical_week_parity)
        db.session.add(new_cohort)
        db.session.commit()
        return new_cohort

    def delete_cohort(self):
        db.session.delete(self)
        db.session.commit()
        