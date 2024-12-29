from app import create_app
from app.models import Teacher, Modulus, Discipline, Cohort, associations


app = create_app()
with app.app_context():
    teacher = Teacher.query.filter_by(id=4).first()

    print(teacher.name)