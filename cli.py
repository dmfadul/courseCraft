from app import create_app
from app.models import Teacher, Modulus, Discipline, Cohort, associations, Classroom, Lecture
import unicodedata
import migration
import json


# app = create_app()
# with app.app_context():
#     cohort_code = "PAP21"
#     new_room_code = "26"
#     alt_room_code = "24"

#     new_room = Classroom.query.filter_by(code=new_room_code).first()
#     alt_room = Classroom.query.filter_by(code=alt_room_code).first()
#     cohort = Cohort.query.filter_by(code=cohort_code).first()
#     disciplines = Discipline.query.all()
#     for disc in disciplines:
#         modulus = Modulus.query.filter_by(discipline_id=disc.id, cohort_id=cohort.id).first()
#         if modulus is None:
#             continue
        
#         print(modulus.code)
#         for lec in modulus.lectures:
#             if not lec.classroom.code in ["24", "26", "28", "32", "34"]:
#                 continue
            
#             if lec.joined_cohorts:
#                 lec.set_classroom(classroom=new_room)
#                 continue

#             test_lec = Lecture.query.filter_by(date=lec.date, grid_position=lec.grid_position).first()
#             if test_lec.classroom_id == 21:
#                 lec.set_classroom(classroom=alt_room)
#                 continue

#             lec.set_classroom(classroom=new_room)
