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
    