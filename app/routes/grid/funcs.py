from flask import flash
from datetime import datetime, timedelta
from app.models import Cohort, Lecture, Classroom, Teacher, Modulus
import app.global_vars as global_vars


def resolve_multiple_lectures_code(lectures):
    if not len(lectures) == 1:
        cohorts = [l.modulus.cohort.code for l in lectures]

        cohorts_dict = {
                        "APJ": [cohort.code for cohort in Cohort.query.all() if "APJ" in cohort.code],
                        "DEL": [cohort.code for cohort in Cohort.query.all() if "DEL" in cohort.code],
                        "PAP": [cohort.code for cohort in Cohort.query.all() if "PAP" in cohort.code],
                        }       

        clean_cohort_code = []
        for key, value in cohorts_dict.items():
            key_cohorts = [cohort for cohort in cohorts if key in cohort]
            if sorted(key_cohorts) == sorted(value):
                clean_cohort_code.append(key)
                continue
            else:
                clean_cohort_code += key_cohorts

        clean_cohort_code = "/".join(sorted(list(set(clean_cohort_code))))
    else:
        clean_cohort_code = lectures[0].modulus.cohort.code

    return clean_cohort_code
    

def gen_empty_grid(week_number):
    starting_date = global_vars.STARTING_DATE + timedelta(weeks=int(week_number) - 1)
    dates = [(starting_date + timedelta(days=i)).strftime("%d/%m") for i in range(len(global_vars.DIAS_DA_SEMANA))]

    grid = [[""] + [str(date) for date in dates] ]
    grid.append([""] + global_vars.DIAS_DA_SEMANA)
    for grid_position in range(global_vars.CLASSES_PER_DAY+global_vars.NUMBER_OF_INTERVALS):
        grid.append([list(global_vars.HOURS_DICT.keys())[grid_position]] + [""] * len(global_vars.DIAS_DA_SEMANA))
    
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if j == 0 and i in [0, 1]:
                grid[i][j] = [grid[i][j], 'corner']
                continue
            if j == 0 and i-2 in global_vars.INTERVALS_SLOTS:
                grid[i][j] = [grid[i][j], 'intervalFirstCol']
                continue
            if j == 0:
                grid[i][j] = [grid[i][j], 'firstColumn']
                continue
            if i == 0:
                grid[i][j] = [grid[i][j], 'header']
                continue
            if i == 1:
                grid[i][j] = [grid[i][j], 'subHeader']
                continue

            date = datetime.strptime(f"{grid[0][j][0]}/{global_vars.SCHOOL_YEAR}", "%d/%m/%Y").date()
        
            # Check for intervals
            if i-2 in global_vars.INTERVALS_SLOTS and date not in global_vars.HOLIDAYS:
                grid[i][j] = ["INTERVALO", "interval"]
                continue

            if i-2 in global_vars.INTERVALS_SLOTS and date in global_vars.HOLIDAYS:
                grid[i][j] = ["", "interval"]
                continue

            if date in global_vars.HOLIDAYS:
                grid[i][j] = ["FERIADO", 'holiday']
                continue

            grid[i][j] = [grid[i][j], '']

    return grid


def gen_empty_matrix(parity, week_number):
    starting_date = global_vars.STARTING_DATE + timedelta(weeks=int(week_number) - 1)
    dates = [(starting_date + timedelta(days=i)).strftime("%d/%m") for i in range(len(global_vars.DIAS_DA_SEMANA))]
    cohorts = Cohort.query.filter_by(theoretical_week_parity=parity).all()
    
    grid = [[""] + [cohort.code for cohort in cohorts] * len(dates)]
    grid.append([""] + [str(date) for date in dates for _ in range(len(cohorts))])
    grid.append([""] + [day for day in global_vars.DIAS_DA_SEMANA for _ in range(len(dates))])

    for grid_position in range(global_vars.CLASSES_PER_DAY+global_vars.NUMBER_OF_INTERVALS):
        grid.append([list(global_vars.HOURS_DICT.keys())[grid_position]] + [""] * len(global_vars.DIAS_DA_SEMANA * len(cohorts)))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if j == 0 and i in [0, 1, 2]:
                grid[i][j] = [grid[i][j], 'corner']
                continue
            if j == 0 and i-2 in global_vars.INTERVALS_SLOTS:
                grid[i][j] = [grid[i][j], 'intervalFirstCol']
                continue
            if j == 0:
                grid[i][j] = [grid[i][j], 'firstColumn']
                continue
            if i == 0:
                grid[i][j] = [grid[i][j], 'header']
                continue
            if i == 1 or i == 2:
                grid[i][j] = [grid[i][j], 'subHeader']
                continue

            date = datetime.strptime(f"{grid[1][j][0]}/{global_vars.SCHOOL_YEAR}", "%d/%m/%Y").date()
        
            # Check for intervals
            if i-2 in global_vars.INTERVALS_SLOTS and date not in global_vars.HOLIDAYS:
                grid[i][j] = ["INTERVALO", "interval"]
                continue

            if i-2 in global_vars.INTERVALS_SLOTS and date in global_vars.HOLIDAYS:
                grid[i][j] = ["", "interval"]
                continue

            if date in global_vars.HOLIDAYS:
                grid[i][j] = ["FERIADO", 'holiday']
                continue

            grid[i][j] = [grid[i][j], '']

    return grid

def gen_matrix(parity, week_number):
    grid = gen_empty_matrix(parity, week_number)
    # grid = gen_empty_grid(week_number)
    
    # for i in range(len(grid)):
    #     for j in range(len(grid[i])):
    #         if j == 0 or i in [0, 1]:
    #             continue
    #         date = datetime.strptime(f"{grid[0][j][0]}/{global_vars.SCHOOL_YEAR}", "%d/%m/%Y").date()
    #         grid_position = global_vars.HOURS_DICT.get(grid[i][0][0])
    #         lectures = Lecture.query.filter_by(date=date, grid_position=grid_position).all()

            
    #         lectures = [lecture for lecture in lectures if lecture.modulus.cohort.code == cohort.code]
        
    #         if lectures:
    #             lecture = lectures[0]
    #             disc_abbr = lecture.modulus.discipline.name_abbr
    #             disc_code = lecture.modulus.discipline.code
    #             teacher_name = lecture.modulus.teachers_names
    #             class_number = Lecture.count(lecture.modulus_id, lecture.date, lecture.grid_position)
    #             workload = lecture.modulus.discipline.workload
    #             classroom = global_vars.LOCAL_OF_CLASSES[0] if lecture.classroom.name == "Externa" else lecture.classroom.name

    #             cell_text = f"""{str(disc_code)}-{disc_abbr}
    #                             {teacher_name}
    #                             {class_number}/{workload}
    #                             {classroom}
    #                         """

    #             if lecture.joined_cohorts:
    #                 cell_formatting = [disc_code.replace(".", "-"), "joined"]
    #             else:
    #                 cell_formatting = disc_code.replace(".", "-")

    #             grid[i][j] = [cell_text, cell_formatting]

    return grid


def gen_lectures_grid(class_code, week_number):
    grid = gen_empty_grid(week_number)

    # Avoid loading unnecessary data
    week_dates = [
        datetime.strptime(f"{day}/{global_vars.SCHOOL_YEAR}", "%d/%m/%Y").date()
        for day, _ in grid[0][1:]
    ]

    lectures = Lecture.query.filter(
        Lecture.date.in_(week_dates)
    ).join(Lecture.modulus).filter(
        Modulus.cohort.has(code=class_code)
    ).all()

    lectures_by_date_position = {
        (lecture.date, lecture.grid_position): lecture for lecture in lectures
    }

    for i in range(len(grid)):
        for j in range(1, len(grid[i])):
            if i in [0, 1]:
                continue

            date = datetime.strptime(f"{grid[0][j][0]}/{global_vars.SCHOOL_YEAR}", "%d/%m/%Y").date()
            grid_position = global_vars.HOURS_DICT.get(grid[i][0][0])

            lecture = lectures_by_date_position.get((date, grid_position))
            if lecture:
                disc_abbr = lecture.modulus.discipline.name_abbr
                disc_code = lecture.modulus.discipline.code
                teacher_name = lecture.modulus.teachers_names
                class_number = Lecture.count(lecture.modulus_id, lecture.date, lecture.grid_position)
                workload = lecture.modulus.discipline.workload
                classroom = (
                    global_vars.LOCAL_OF_CLASSES[0]
                    if lecture.classroom.name == "Externa"
                    else lecture.classroom.name
                )

                cell_text = f"""{disc_code}-{disc_abbr}
                                {teacher_name}
                                {class_number}/{workload}
                                {classroom}
                            """

                cell_formatting = [disc_code.replace(".", "-"), "joined"] if lecture.joined_cohorts else disc_code.replace(".", "-")
                grid[i][j] = [cell_text, cell_formatting]

    return grid


def gen_teacher_schedule(teacher_name, month):
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    inverted_hours_dict = {v: k for k, v in global_vars.HOURS_DICT.items()}
    if not teacher:
        return [[["Professor não encontrado", ""]]]
    
    lectures = sorted(teacher.lectures, key=lambda x: (x.date, x.grid_position))
    lectures = [lecture for lecture in lectures if lecture.date.month == int(month)]

    if not lectures:
        return [[["Sem aulas neste mês", ""]]]

    unique_dates = sorted(list(set([lecture.date for lecture in lectures])))

    lec_dates = [d.strftime("%d/%m") for d in unique_dates]
    lec_weekdays = [d.weekday() for d in unique_dates]
    
    dates = [["", "corner"]] + [list((date, "header")) for date in lec_dates]
    week_days = [["", "corner"]] + [list((global_vars.DIAS_DA_SEMANA[weekday], "subHeader")) for weekday in lec_weekdays]
    
    grid = []
    grid.append(dates)
    grid.append(week_days)

    lectures = sorted(lectures, key=lambda x: (x.grid_position, x.date))
    str_hours = []
    for lecture in lectures:
        str_hour = inverted_hours_dict.get(lecture.grid_position)
        if str_hour in str_hours:
            continue
        
        str_hours.append(str_hour)
        row = [[str_hour, ""]] + [["", ""]] * len(lec_dates)
        grid.append(row)

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if j == 0 or i in [0, 1]:
                continue

            date = datetime.strptime(f"{grid[0][j][0]}/{global_vars.SCHOOL_YEAR}", "%d/%m/%Y").date()
            grid_position = global_vars.HOURS_DICT.get(grid[i][0][0])
            
            lectures = [l for l in teacher.all_lectures if (l.date==date and l.grid_position==grid_position)]

            if not len(lectures) == 1 and not all([l.joined_cohorts for l in lectures]):
                cohort_code = resolve_multiple_lectures_code(lectures)

                cell_text = "CONFLITO\n"
                for lecture in lectures:
                    disc_abbr = lecture.modulus.discipline.name_abbr
                    disc_code = lecture.modulus.discipline.code

                    cell_text += f"{str(disc_code)}-{disc_abbr}\n"

                cell_text += f"{cohort_code}"
                grid[i][j] = [cell_text, disc_code.replace(".", "-")]
                
            elif lectures:
                lecture = lectures[0]
                disc_abbr = lecture.modulus.discipline.name_abbr
                disc_code = lecture.modulus.discipline.code
                cohort_code = resolve_multiple_lectures_code(lectures)
                classroom = global_vars.LOCAL_OF_CLASSES[0] if lecture.classroom.name == "Externa" else lecture.classroom.name

                cell_text = f"""{str(disc_code)}-{disc_abbr}
                                {cohort_code}
                                {classroom}
                            """
                
                grid[i][j] = [cell_text, disc_code.replace(".", "-")]

    return grid


def gen_classroom_schedule(classroom_name, week_number):
    grid = gen_empty_grid(week_number)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if j == 0 or i in [0, 1]:
                continue

            date = datetime.strptime(f"{grid[0][j][0]}/{global_vars.SCHOOL_YEAR}", "%d/%m/%Y").date()
            grid_position = global_vars.HOURS_DICT.get(grid[i][0][0])

            classroom = Classroom.query.filter_by(name=classroom_name).first()
            if not classroom or not classroom.lectures:
                return grid
            
            lectures = [l for l in classroom.lectures if (l.date==date and l.grid_position==grid_position)]
            if not len(lectures) == 1 and not all([l.joined_cohorts for l in lectures]):
                raise Exception("Erro. Há mais de uma aula na mesma sala, data e horário.")

            if lectures:
                lecture = lectures[0]
                disc_abbr = lecture.modulus.discipline.name_abbr
                disc_code = lecture.modulus.discipline.code
                teacher_name = lecture.modulus.teachers_names
                cohort_code = resolve_multiple_lectures_code(lectures)

                cell_text = f"""{str(disc_code)}-{disc_abbr}
                                {teacher_name}
                                {cohort_code}
                            """
                
                grid[i][j] = [cell_text, disc_code.replace(".", "-")]

    return grid


def populate_discipline_list(class_code, parity, get_all=False):
    cohort = Cohort.query.filter_by(code=class_code).first()

    moduli = cohort.moduli
    if not get_all:
        moduli = [modulus for modulus in moduli if not modulus.discipline.is_theoretical == parity]   
    moduli = [modulus for modulus in moduli if not modulus.is_complete]
    
    moduli = sorted(
        moduli,
        key=lambda x: (
            float('.'.join(part.zfill(2) for part in x.discipline.code.replace('P', '').split('.'))),  # Pad fractions
            'P' in x.discipline.code  # Place 'P' codes after non-'P' codes
        )
    )

    discipline_list = ["0 - APAGAR"] + [f"{modulus.discipline.code} - {modulus.discipline.name} ({modulus.remaining_workload}/{modulus.discipline.workload})" for modulus in moduli]
    

    return discipline_list


def resolve_lectures(data):
    from .validation import check_conflicting_classrooms, check_teachers_availability, check_for_intensive_classes

    data = sorted(data, key=lambda x: x['columnIndex'])
    class_code = data[0]['classCode']
    discipline = data[0]['selectedOption'].split(" - ")[0].strip()
    classroom = None if data[0]['selectedClassroom'] == "-" else data[0]['selectedClassroom']
    starting_week = data[0]['startingWeek']
    starting_date = global_vars.STARTING_DATE + timedelta(weeks=int(starting_week) - 1)
    action = "delete" if data[0].get("selectedOption").split(" - ")[0] == "0" else "add"
    repeat_weekly = data[0]['repeatWeekly']
    joined_cohorts = data[0]['joinCohorts']
    forced = data[0]['forced']
    get_all_disciplines = data[0]['getAllDisciplines']
    
    while True:
        for datum in data:
            grid_position = global_vars.HOURS_DICT.get(datum['rowId'].strip())
            dates = [""] + [(starting_date + timedelta(days=i)).strftime("%d/%m") for i in range(len(global_vars.DIAS_DA_SEMANA))]
            date_str = dates[datum['columnIndex']] + "/" + global_vars.SCHOOL_YEAR
            date = datetime.strptime(date_str, "%d/%m/%Y").date()
                
            if date in global_vars.HOLIDAYS:
                continue

            if date > global_vars.ENDING_DATE:
                print("Data final atingida")
                return 0

            existing_lectures = Lecture.query.filter_by(grid_position=grid_position, date=date).all()
            existing_lectures = [l for l in existing_lectures if l.modulus.cohort.code == class_code]

            if existing_lectures and repeat_weekly and action == "delete":
                modulus = existing_lectures[0].modulus
                all_lectures = Lecture.query.filter_by(modulus_id=modulus.id).all()

                if all_lectures:
                    for lecture in all_lectures:
                        lecture.delete_lecture()
                return 0
            
            if existing_lectures:
                for lecture in existing_lectures:
                    if action == "add":
                        flash(f"Já existe aula marcada para {lecture.date}, {lecture.grid_position}.", "danger")
                        continue
                    else:
                        lecture.delete_lecture()

            if not action == "add":
                continue

            lecture = Lecture.add_lecture(date=date,
                                          grid_position=grid_position,
                                          class_code=class_code,
                                          discipline_code=discipline,
                                          joined=joined_cohorts)
            if lecture == 1:
                print("Disciplina completa")
                return 0
            
            if lecture == -1:
                print(f"Já existe aula marcada para data e hora.")
                flash(f"Já existe aula marcada para data, hora e turma.", "danger")
                continue

            if classroom:
                lecture.change_classroom(classroom)
            else:
                lecture.set_classroom()

            if forced:
                classroom_flag = None
                teacher_flag = None
                intensive_flag = None
            else:
                classroom_flag = check_conflicting_classrooms(lecture)
                teacher_flag = check_teachers_availability(lecture)
                intensive_flag = check_for_intensive_classes(lecture)

            if classroom_flag:
                lecture.delete_lecture()
                return 0
            
            if teacher_flag:
                lecture.delete_lecture()
                return 0
            
            if intensive_flag:
                lecture.delete_lecture()
                return 0

        week_increment = 1 if (get_all_disciplines or not global_vars.ALTERNATING_WEEKS) else 2
        starting_date = starting_date + timedelta(weeks=week_increment) 
        if not repeat_weekly:
            break

    return 0    
