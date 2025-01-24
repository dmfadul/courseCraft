from app import db


class Classroom(db.Model):
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    fungible = db.Column(db.Boolean, nullable=False, default=True)
    capacity = db.Column(db.Integer, nullable=False)

    disciplines = db.relationship('Discipline', back_populates='mandatory_room')
    moduli = db.relationship('Modulus', back_populates='classroom')
    lectures = db.relationship('Lecture', back_populates='classroom')

    @classmethod
    def add_classroom(cls, code, name, capacity, fungible=True):
        new_classroom = cls(name=name, code=code, capacity=capacity, fungible=fungible)
        db.session.add(new_classroom)
        db.session.commit()
        return new_classroom

    def delete_classroom(self):
        db.session.delete(self)
        db.session.commit()
        return 0
    
    def check_for_conflicts(self):
        conflicting_lectures = []
        for i in range(len(self.lectures)-1):
            for j in range(i+1, len(self.lectures)):
                test_l = self.lectures[i]
                target_l = self.lectures[j]

                if test_l.date == target_l.date and test_l.grid_position == target_l.grid_position:
                    test_disc_id = test_l.modulus.discipline_id
                    target_disc_id = target_l.modulus.discipline_id
                    if test_l.joined_cohorts and target_l.joined_cohorts and (test_disc_id == target_disc_id):
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