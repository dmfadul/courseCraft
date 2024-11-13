from app import db
from sqlalchemy import ForeignKey


teacher_discipline_association = db.Table(
    'teacher_discipline_association', 
    db.Model.metadata,
    db.Column('teacher_id', db.Integer, ForeignKey('teachers.id')),
    db.Column('discipline_id', db.Integer, ForeignKey('disciplines.id'))
)

teacher_modulus_association = db.Table(
    'teacher_modulus_association',
    db.Model.metadata,
    db.Column('teacher_id', db.Integer, ForeignKey('teachers.id')),
    db.Column('modulus_id', db.Integer, ForeignKey('moduli.id'))
)

cohort_discipline_association = db.Table(
    'cohorts_disciplines',
    db.Model.metadata,
    db.Column('cohort_id', db.Integer, ForeignKey('cohorts.id')),
    db.Column('discipline_id', db.Integer, ForeignKey('disciplines.id'))
)

discipline_prerequisite_association = db.Table(
    'discipline_prerequisites',
    db.Model.metadata,
    db.Column('discipline_code', db.String(20), ForeignKey('disciplines.code'), primary_key=True),
    db.Column('prerequisite_code', db.String(20), ForeignKey('disciplines.code'), primary_key=True)
)
