from app.models import Teacher, Modulus, Lecture, Classroom, Discipline, Cohort
import app.global_vars as global_vars


def check_lectures_in_wrong_week():
    from app.global_vars import ALTERNATING_WEEKS

    if not ALTERNATING_WEEKS:
        return [[["NESTE CURSO AS SEMANAS NÃO SÃO ALTERNADAS", "name"]]]
    
    moduli = Modulus.query.all()

    misplaced_lectures = []
    for modulus in moduli:
        for lecture in modulus.lectures:
            time_delta = lecture.date - global_vars.STARTING_DATE
            week_parity = (time_delta.days//7 + 1)%2
            mod_parity = modulus.cohort.theoretical_week_parity

            if lecture.joined_cohorts:
                continue
            if modulus.discipline.is_theoretical and week_parity == mod_parity:
                continue
            if not modulus.discipline.is_theoretical and week_parity != mod_parity:
                continue
            
            misplaced_lectures.append(lecture)

    grid = [[[]]]

    for lec in misplaced_lectures:
        grid.append([[f"{lec.modulus.code} -- {lec.date}", "name"]])

    return grid


def list_moduli_workload():
    moduli = Modulus.query.all()

    moduli_grid = [[["módulo", 'normal'], ["C.H.", 'normal']]]
    for mod in moduli:
        if mod.remaining_workload == 0:
            continue
        
        name = mod.discipline.name
        code = mod.discipline.code
        cohort_code = mod.cohort.code
        new_row = [[f"{code} - {name} - {cohort_code}", "name"]]
        workload = mod.remaining_workload
        formatting = "overwork" if workload < 0 else "normal"
        new_row.append([workload, formatting])
        moduli_grid.append(new_row)

    return moduli_grid


def list_total_hours():
    lectures = Lecture.query.all()
    unique_lecs = []
    for lec in lectures:
        if '0.' in lec.modulus.discipline.code:
            continue
        lec_tuple = (lec.date,
                     lec.grid_position,
                     lec.modulus.discipline.name,
                     lec.classroom_id)
        if lec_tuple not in unique_lecs:
            unique_lecs.append(lec_tuple)

    print(len(lectures))
    print(len(unique_lecs))
    return 0

def calculate_teachers_workload():
    from app.global_config import TEACHERS_MAX_HOURS_PER_MONTH as max_hours
    teachers = Teacher.query.all()
    teachers = sorted(teachers, key=lambda x: x.name)
    meses_in_course = [global_vars.MESES_ABR[int(m)-1] for m in global_vars.MONTHS]

    teacher_grid = [[["Professor", "normal"]] + [[m, "normal"] for m in meses_in_course]]
    for teacher in teachers:
        if len(teacher.lectures) == 0:
            continue

        new_row = [[teacher.name, "name"]]
        for month in global_vars.MONTHS:
            workload = teacher.workload(int(month))
            formatting = "overwork" if workload >= max_hours else "normal"
            new_row.append([workload, formatting])
        teacher_grid.append(new_row)

    return teacher_grid
        

def check_moduli_workload():
    moduli = Modulus.query.all()
    for modulus in moduli:
        if modulus.current_workload == 0:
            continue

        print(modulus.code, modulus.current_workload)


def check_classes_for_teachers():
    moduli = Modulus.query.all()

    grid = []
    if not moduli:
        print("No Moduli found")
        return grid
    
    for modulus in moduli:
        if not modulus.teachers:
            grid.append([[f"{modulus.discipline.name} -- {modulus.cohort.code}", "name"]])
        else:
            print(modulus.code, modulus.teachers_names)
    return grid


def check_classes_for_classrooms():
    moduli = Modulus.query.all()

    grid = []
    if not moduli:
        print("No Moduli found")
        return grid
    
    for modulus in moduli:
        if modulus.classroom.code == "0":
            grid.append([[f"{modulus.discipline.name} -- {modulus.cohort.code}", "name"]])

    grid.append([["Nenhuma Aula sem Sala", "name"]])

    return grid


def check_proximity_of_intensive_moduli():
    lectures = Lecture.query.all()
    lectures = [l for l in lectures if l.modulus.discipline.is_intensive]

    grid = [[[]]]
    for i in range(len(lectures)-1):
        discipline_id = lectures[i].modulus.discipline.id
        date = lectures[i].date
        
        if discipline_id==lectures[i+1].modulus.discipline.id:
            print(discipline_id)
            continue

        for j in range(i+1, len(lectures)):


            if date==lectures[j].date:           
                grid.append([[f"""{lectures[j].modulus.discipline.name} --
                               {lectures[j].modulus.cohort.code} --
                               {date}""", "name"]])

    return grid


def check_prerequisites():
    moduli = Modulus.query.all()
    moduli = [m for m in moduli if (m.lectures and m.discipline.prerequisites)]

    unique_grid = []
    for modulus in moduli:
        for prerequisite in modulus.discipline.prerequisites:
            prereq_modulus = Modulus.query.filter_by(discipline_id=prerequisite.id, cohort_id=modulus.cohort_id).first()

            if not prereq_modulus or prereq_modulus.end_date == -1 or prereq_modulus.end_date < modulus.start_date:
                if not modulus.code in unique_grid:
                    unique_grid.append(modulus.code)

    grid = [[[]]]
    for code in unique_grid:
        grid.append([[code, "name"]])

    return grid


def check_lectures_in_odd_classrooms():
    lectures = Lecture.query.all()

    grid = [[[]]]
    for lecture in lectures:
        if not lecture.classroom.id == lecture.modulus.main_classroom_id:
            supposed_room = Classroom.query.filter_by(id=lecture.modulus.main_classroom_id).first()
            message = f"""{lecture.modulus.discipline.name} --
                          {lecture.modulus.cohort.code} --
                          {lecture.date} --
                          {lecture.grid_position} --
                          Marcada para {lecture.classroom.code} --
                          Deveria ser {supposed_room.name}"""
            grid.append([[message, "name"]])

    return grid



def list_teachers_by_cohorts():
    disciplines = Discipline.query.all()
    disciplines = Discipline.sort_by_code(disciplines)

    grid = []
    for disc in disciplines:
        if '0' in disc.code:
            continue
        
        grid.append([[f"{disc.code} - {disc.name.upper()}:", "name"]])
        for mod in disc.moduli:
            teachers_names = sorted([t.name for t in mod.teachers])
            teachers_names = '' if not teachers_names else ', '.join(teachers_names)
            grid.append([[f"{mod.cohort.code} - {teachers_names}", "name"]])

    return grid


def check_for_classroom_conflicts():
    classrooms = Classroom.query.all()

    grid = []
    for classroom in classrooms:
        flag = classroom.check_for_conflicts()
        if flag == 0:
            continue

        grid.append([[f"{classroom.name}:", "name"]])

        for line in flag:
            grid.append([[f"{line}", "name"]])

    if not grid:
        return [[["no conflicts found", "name"]]]

    return grid


def check_teachers_conflicts():
    teachers = Teacher.query.all()

    grid = []    
    for teacher in teachers:
        flag = teacher.check_for_conflicts()
        if flag == 0:
            continue
        
        grid.append([[f"{teacher.name}:", "name"]])

        for line in flag:
            grid.append([[f"{line}", "name"]])

    if not grid:
        return [[["No conflicts found", "name"]]]

    return grid
    