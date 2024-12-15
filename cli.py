from t_list import teacher_list
from app import create_app
from app.models import Teacher, Modulus, Discipline, Cohort, associations
import unicodedata
import migration
import json


def add_teachers_from_dict():
    from app.routes.grid.validation import check_teacher_conflicts
    app = create_app()
    wrong_names = []
    for entry in teacher_list:
        code = entry.get("code")
        t_names = entry.get("teachers")
        cohorts_str = entry.get("cohorts")
        cohorts_lst = cohorts_str.split("+")
        cohorts_lst = [c.strip() for c in cohorts_lst]
    
        cohorts_lst = ['PAP21' if c == 'PAP' else c for c in cohorts_lst]
        cohorts_lst = ['DEL44' if c == 'DEL' else c for c in cohorts_lst]
    
        cohorts_lst = [
            sub_item
            for item in cohorts_lst
            for sub_item in (["APJ04", "APJ05", "APJ06"] if item == "APJ" else [item])
        ]
    
        with app.app_context():   
            discipline = Discipline.query.filter_by(code=code).first()
            if discipline is None:
                print(f"Discipline {code} not found.")
                continue
            
            for c in cohorts_lst:
                cohort = Cohort.query.filter_by(code=c).first()
                if cohort is None:
                    print(f"Cohort {c} not found.")
                    continue
                
                modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
                if modulus is None:
                    print(f"Modulus {code}-{c} not found.")
                    continue
    
                for name in t_names:
                    if name == "":
                        continue
            
                    clean_name = ' '.join([name.capitalize().strip() for name in name.split(' ')])
                    clean_name = unicodedata.normalize('NFKD', clean_name).encode('ASCII', 'ignore').decode('utf-8')
                    teacher = Teacher.query.filter_by(name=clean_name).first()
                    if teacher is None:
                        print(f"Teacher {clean_name} not found.")
                        continue
    
                    if teacher not in discipline.teachers:
                        print(f"Teacher {teacher.name} not allowed to teach {discipline.name}.")
                        continue
    
                    if teacher not in modulus.teachers:
                        flag1 = check_teacher_conflicts(teacher, modulus)
                        if not flag1 == 0:
                            print(flag1)
                            continue
                        flag2 = modulus.add_teacher(teacher.name)
                        print(flag2)
                        

def check_modulus(disc, coh):
    app = create_app()
    wrong_names = []
    for entry in teacher_list:
        code = entry.get("code")
        t_names = entry.get("teachers")
        cohorts_str = entry.get("cohorts")
        cohorts_lst = cohorts_str.split("+")
        cohorts_lst = [c.strip() for c in cohorts_lst]

        cohorts_lst = ['PAP21' if c == 'PAP' else c for c in cohorts_lst]
        cohorts_lst = ['DEL44' if c == 'DEL' else c for c in cohorts_lst]

        cohorts_lst = [
            sub_item
            for item in cohorts_lst
            for sub_item in (["APJ04", "APJ05", "APJ06"] if item == "APJ" else [item])
        ]

        with app.app_context():
            discipline_test = Discipline.query.filter_by(code=disc).first()
            cohort_test = Cohort.query.filter_by(code=coh).first()
            modulus_test = Modulus.query.filter_by(discipline_id=discipline_test.id, cohort_id=cohort_test.id).first()

            discipline = Discipline.query.filter_by(code=code).first()
            if discipline is None:
                print(f"Discipline {code} not found.")
                continue

            for c in cohorts_lst:
                cohort = Cohort.query.filter_by(code=c).first()
                if cohort is None:
                    print(f"Cohort {c} not found.")
                    continue

                modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
                if modulus is None:
                    print(f"Modulus {code}-{c} not found.")
                    continue
                
                flag = modulus_test.check_for_modulus_conflict(modulus.discipline.id, modulus.cohort.id)

                if len(flag) == 0:
                    continue
                
                if isinstance(flag, str):
                    print(flag)
                    continue

                for lec1, lec2 in flag:
                    part1 = f"{lec1.date} - {lec1.grid_position}."
                    part2 = f"{lec1.modulus.discipline.code} - {lec1.modulus.discipline.name_abbr}/{lec1.modulus.cohort.code}"
                    part3 = f"{lec2.modulus.discipline.code} - {lec2.modulus.discipline.name_abbr}/{lec2.modulus.cohort.code}"
                    print(f"{part1} {part2} // {part3}")

def check_all():
    for entry in teacher_list:
        code = entry.get("code")
        cohorts_str = entry.get("cohorts")
        cohorts_lst = cohorts_str.split("+")
        cohorts_lst = [c.strip() for c in cohorts_lst]

        cohorts_lst = ['PAP21' if c == 'PAP' else c for c in cohorts_lst]
        cohorts_lst = ['DEL44' if c == 'DEL' else c for c in cohorts_lst]

        cohorts_lst = [
        sub_item
        for item in cohorts_lst
        for sub_item in (["APJ04", "APJ05", "APJ06"] if item == "APJ" else [item])
        ]

        app = create_app()
        with app.app_context():
            discipline = Discipline.query.filter_by(code=code).first()
            if discipline is None:
                print(f"Discipline {code} not found.")
                continue

            for c in cohorts_lst:
                cohort = Cohort.query.filter_by(code=c).first()
                if cohort is None:
                    print(f"Cohort {c} not found.")
                    continue

                modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
                if modulus is None:
                    print(f"Modulus {code}-{c} not found.")
                    continue
                
                print(f"Checking {modulus.discipline.code} - {modulus.discipline.name_abbr}...")
                check_modulus(discipline.code, cohort.code)
                print("\n\n")

add_teachers_from_dict()
# check_all()

# app = create_app()
# with app.app_context():
#     discipline = Discipline.query.filter_by(code="5.3").first()
#     # cohort = Cohort.query.filter_by(code="APJ05").first()
#     print(discipline.name)
#     discipline.remove_all_teachers()
#     # modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
#     # print(modulus.code)
#     # modulus.clear_teachers()