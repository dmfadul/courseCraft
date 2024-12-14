from t_list import teacher_list
from app import create_app
from app.models import Teacher, Modulus, Discipline, Cohort, associations
import unicodedata
import migration
import json

app = create_app()
with app.app_context():
    discipline1 = Discipline.query.filter_by(code='5.6').first()
    cohort1 = Cohort.query.filter_by(code='DEL44').first()
    modulus1 = Modulus.query.filter_by(discipline_id=discipline1.id, cohort_id=cohort1.id).first()

    discipline2 = Discipline.query.filter_by(code='5.3').first()
    cohort2 = Cohort.query.filter_by(code='APJ04').first()
    modulus2 = Modulus.query.filter_by(discipline_id=discipline2.id, cohort_id=cohort2.id).first()

    conflicts = modulus1.check_for_modulus_conflict(modulus2.discipline.id, modulus2.cohort.id)
    for lec1, lec2 in conflicts:
        print(f"{lec1.date} - {lec1.grid_position}. {lec1.modulus.discipline.name}/{lec1.modulus.cohort.code} - {lec2.modulus.discipline.name}/{lec2.modulus.cohort.code}")

# app = create_app()
# wrong_names = []
# for entry in teacher_list:
#     code = entry.get("code")
#     t_names = entry.get("teachers")
#     cohorts_str = entry.get("cohorts")
#     cohorts_lst = cohorts_str.split("+")
#     cohorts_lst = [c.strip() for c in cohorts_lst]

#     cohorts_lst = ['PAP21' if c == 'PAP' else c for c in cohorts_lst]
#     cohorts_lst = ['DEL44' if c == 'DEL' else c for c in cohorts_lst]

#     cohorts_lst = [
#         sub_item
#         for item in cohorts_lst
#         for sub_item in (["APJ04", "APJ05", "APJ06"] if item == "APJ" else [item])
#     ]

#     with app.app_context():
#         discipline = Discipline.query.filter_by(code=code).first()
#         if discipline is None:
#             print(f"Discipline {code} not found.")
#             continue

#         for c in cohorts_lst:
#             cohort = Cohort.query.filter_by(code=c).first()
#             if cohort is None:
#                 print(f"Cohort {c} not found.")
#                 continue

#             modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
#             if modulus is None:
#                 print(f"Modulus {code}-{c} not found.")
#                 continue
            
            # flag = modulus.check_for_modulus_conflict(modulus.discipline.id, modulus.cohort.id)
            
            # for name in t_names:
            #     if name == "":
            #         continue
        
            #     clean_name = ' '.join([name.capitalize().strip() for name in name.split(' ')])
            #     clean_name = unicodedata.normalize('NFKD', clean_name).encode('ASCII', 'ignore').decode('utf-8')
            #     teacher = Teacher.query.filter_by(name=clean_name).first()
            #     if teacher is None:
            #         print(f"Teacher {clean_name} not found.")
            #         continue

            #     if teacher not in discipline.teachers:
            #         print(f"Teacher {teacher.name} not allowed to teach {discipline.name}.")
            #         continue

                # if teacher not in modulus.teachers:
                    # flag = teacher.check_for_conflict()
                #     flag = modulus.add_teacher(teacher.name)
                #     print(flag)
                    