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

    def check_for_conflicts(self):
        conflicting_lectures = []
        for i in range(len(self.all_lectures)-1):
            for j in range(i+1, len(self.all_lectures)):
                test_l = self.all_lectures[i]
                target_l = self.all_lectures[j]

                if test_l.date == target_l.date and test_l.grid_position == target_l.grid_position:
                    if test_l.joined_cohorts and target_l.joined_cohorts and (test_l.classroom_id == target_l.classroom_id):
                        continue
                    if test_l == target_l:
                        continue
                    conflicting_lectures.append((test_l, target_l))

        if not conflicting_lectures:
            return 0

        output, done = [], []
        for test_l, target_l in conflicting_lectures:
            if test_l in done:
                continue

            output.append(f"""{test_l.modulus.discipline.name} - {test_l.date}, {test_l.grid_position} - 
            entre as turmas {test_l.modulus.cohort.code} e {target_l.modulus.cohort.code}.""")
            
            done.append(test_l)

        return output
      
    def check_for_conflict(self, date, grid_position, joined=False):
        for lecture in self.all_lectures:
            if lecture.date == date and lecture.grid_position == grid_position:
                if lecture.joined_cohorts and joined:
                    return 0
                return f"Teacher {self.name} is already teaching {lecture.discipline.name} at {date} - {grid_position}."
        return 0