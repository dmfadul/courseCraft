from app import create_app
from app.models import Teacher, Modulus, Discipline, Cohort
import migration


# app = create_app()
# with app.app_context():
#     disciplines = Discipline.query.all()
#     for discipline in disciplines:
#         for modulus in discipline.moduli:
#             modulus.clear_teachers()
#             print(modulus.code, modulus.teachers_names)


# migration.add_users()
# migration.add_teachers()
# migration.add_cohorts()
# migration.add_classrooms()
# migration.add_disciplines()
# migration.add_prerequisites()
# migration.add_moduli()
# migration.add_teacher_to_modulus()
# migration.gen_teacher_moduli_dict()

    
# moduli = Modulus.query.all()
# for modulus in moduli:
#     print(modulus.code, modulus.teachers_names)

# disciplines = Discipline.query.all()
# for discipline in disciplines:
#     print(discipline.name, discipline.mandatory_room)
#     for modulus in discipline.moduli:
#         print(modulus.code, modulus.classroom)

# teachers = Teacher.query.all()
# print(teachers[0].name, teachers[0].lectures)
# print(teachers[1].name, teachers[1].lectures)
