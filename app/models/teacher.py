from app import db
from .discipline import Discipline
from sqlalchemy.orm import relationship
from .associations import teacher_discipline_association, teacher_modulus_association


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    abbr_name = db.Column(db.String(40), nullable=False)
    rg = db.Column(db.String(20), nullable=False, unique=True)

    disciplines = relationship(
        'Discipline', 
        secondary=teacher_discipline_association, 
        back_populates='teachers'
    )
    
    moduli = relationship(
        'Modulus',
        secondary=teacher_modulus_association,
        back_populates='teachers',
    )

    @classmethod
    def add_teacher(cls, name, abbr_name, rg):
        name = ' '.join([name.capitalize().strip() for name in name.split(' ')])
        abbr_name = ' '.join([name.capitalize().strip() for name in abbr_name.split(' ')])
        rg = rg.replace('.', '').replace('-', '')

        check_name = cls.query.filter_by(name=name).first()
        check_rg = cls.query.filter_by(rg=rg).first()

        if check_name:
            print('Teacher already exists')
            return 1
        if check_rg:
            print('RG already exists')
            return 2
        
        new_teacher = cls(name=name, abbr_name=abbr_name, rg=rg)
        db.session.add(new_teacher)
        db.session.commit()

        return new_teacher

    @property
    def all_lectures(self):
        lectures = []
        for modulus in self.moduli:
            for lecture in modulus.lectures:
                lectures.append(lecture)

        return lectures
    
    @property
    def lectures(self):
        lectures = self.all_lectures

        unique_lectures = []
        for l in lectures:
            if (l.date, l.grid_position) not in [(ul.date, ul.grid_position) for ul in unique_lectures]:
                unique_lectures.append(l)

        return unique_lectures
    
    def workload(self, month):
        workload = 0
        for lecture in self.lectures:
            if lecture.date.month == month:
                workload += 1

        return workload

    def delete_teacher(self):
        db.session.delete(self)
        db.session.commit()

    def edit(self, name):
        self.name = name
        db.session.commit()

    def add_discipline(self, discipline_code):
        discipline = Discipline.query.filter_by(code=discipline_code).first()
        if discipline not in self.disciplines:
            self.disciplines.append(discipline)
            db.session.commit()
