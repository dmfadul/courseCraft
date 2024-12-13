from t_list import teacher_list
from app import create_app
from app.models import Teacher, Modulus, Discipline, Cohort, associations
import unicodedata
import migration
import json


# app = create_app()
# with app.app_context():
#     moduli = Modulus.query.all()

#     for modulus in moduli:
#         modulus.clear_teachers()



app = create_app()
wrong_names = []
for entry in teacher_list:
    code = entry.get("code")
    t_names = entry.get("teachers")

    with app.app_context():
        for name in t_names:
            if name == "":
                continue
            
            clean_name = ' '.join([name.capitalize().strip() for name in name.split(' ')])
            clean_name = unicodedata.normalize('NFKD', clean_name).encode('ASCII', 'ignore').decode('utf-8')
            teacher = Teacher.query.filter_by(name=clean_name).first()
            if teacher is None:
                if clean_name not in wrong_names:
                    wrong_names.append(clean_name)
                
if wrong_names:
    wrong_names = sorted(list(set(wrong_names)))
    for i, name in enumerate(wrong_names):
        print(i+1, name)



        # disc = Discipline.query.filter_by(code=code).first()
        # if disc is None:
        #     print(code)


# app = create_app()
# with app.app_context():
    # new_disc = Discipline.add_discipline(
    #                                     name="AVALIAÇÕES DAS DISCIPLINAS E DA CPA",
    #                                     name_abbr="AVAL. DISC. E CPA",
    #                                     code="6.13",
    #                                     workload=4,
    #                                     is_theoretical=True,
    #                                     is_intensive=False,
    #                                     mandatory_room=None,
    #                                     teachers=None,
    #                                     joined_cohorts=False)

    # disc_code = "6.7"
    # cohort_code = "APJ04"
    # teacher_name = "David Fadul"

    # disc = Discipline.query.filter_by(code=disc_code).first()
    # cohort = Cohort.query.filter_by(code=cohort_code).first()
    # teacher = Teacher.query.filter_by(name=teacher_name).first()

    # mod = Modulus.query.filter_by(discipline_id=disc.id, cohort_id=cohort.id).first()
    # mod.add_teacher(teacher.name)

    # print(teacher.name)
    # print(disc.name)
    # print(mod.code)

    # disc.add_teacher(teacher.name)

    # for t in disc.teachers:
    #     print(t.name)

    # print(disc.name)
    # for teacher in disc.teachers:
        # print(teacher.name)

# migration.add_users()
# migration.add_teachers()
# migration.add_cohorts()
# migration.add_classrooms()
# migration.add_disciplines()
# migration.add_prerequisites()
# migration.add_moduli()

# migration.gen_teacher_moduli_dict()

# migration.add_teacher_to_modulus()


    
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
