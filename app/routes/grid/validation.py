from flask import flash
from app.models import Lecture


def check_classroom_availability(classroom, modulus):
    common_lectures = []
    for c_lecture in classroom.lectures:
        for m_lecture in modulus.lectures:
            if c_lecture.date == m_lecture.date and c_lecture.grid_position == m_lecture.grid_position:
                common_lectures.append(c_lecture)

    if not common_lectures:
        print("No conflicts found.")
        return 0
    
    message = f"{classroom.name} está ocupado(a) nas seguintes aulas: <br>"
    for lecture in common_lectures:
        cohort_code = lecture.modulus.cohort.code
        message += f"""{lecture.date}, {lecture.grid_position} na turma {lecture.modulus.cohort.code}."""
        message += "<br>"

    return message


def check_conflicting_classrooms(lecture):
    if lecture.classroom.code == "0":
        print("Classroom not yet assigned.")
        return 0

    if lecture.classroom.code == "-1":
        print("External Lecture. No need to check for classroom conflicts.")
        return 0
    
    date = lecture.date
    grid_position = lecture.grid_position
    t_lectures = Lecture.query.filter_by(date=date, grid_position=grid_position).all()
    t_lectures = [l for l in t_lectures if not l.id == lecture.id]
    conflict_lectures = [l for l in t_lectures if l.classroom.code == lecture.classroom.code]
    
    if not conflict_lectures:
        print("No conflicts found.")
        return 0
    
    if not lecture.joined_cohorts:
        conflict_lecture = conflict_lectures[0]
        message = f"""{lecture.classroom.name} está ocupada
                   pela turma {conflict_lecture.modulus.cohort.code}
                   com a disciplina {conflict_lecture.modulus.discipline.name}."""

        flash(message, 'danger')
        return 1
    
    if not all([l.joined_cohorts for l in conflict_lectures]):
        conflict_lecture = [l for l in conflict_lectures if not l.joined_cohorts][0]
        message = f"""{lecture.classroom.name} está ocupada 
                    por aula NÃO CONJUNTA da turma:
                    {conflict_lecture.modulus.cohort.code}."""
        
        flash(message, 'danger')
        return 1
    
    if not all([l.modulus.discipline.id == lecture.modulus.discipline.id for l in conflict_lectures]):
        message = f"""{lecture.classroom.name} está ocupada 
                    por aula conjunta, mas de disciplina diferente."""
        
        flash(message, 'danger')
        return 1

    print("All lectures in the classroom are joined cohorts.")
    return 0


def check_teacher_conflicts(teacher, modulus):
    message = ""
    common_lectures = []
    for t_lecture in teacher.lectures:
        for m_lecture in modulus.lectures:
            same_date = t_lecture.date == m_lecture.date
            same_position = t_lecture.grid_position == m_lecture.grid_position 
            same_room = t_lecture.classroom_id == m_lecture.classroom_id
            if same_date and same_position:
                if same_room and t_lecture.joined_cohorts and m_lecture.joined_cohorts:
                    continue
                
                common_lectures.append(t_lecture)

    if not common_lectures:
        # print("No conflicts found.")
        return 0
    
    message = f"O professor(a) {teacher.name} está ocupado(a) nas seguintes aulas: <br>"
    for lecture in common_lectures:
        message += f"""{lecture.date}, {lecture.grid_position} na turma {lecture.modulus.cohort.code}."""
        message += "<br>"

    return message


def check_teachers_availability(lecture):
    if len(lecture.modulus.teachers) == 0: 
        print("Teacher not yet assigned.")
        return 0
    
    date = lecture.date
    grid_position = lecture.grid_position
    t_lectures = Lecture.query.filter_by(date=date, grid_position=grid_position).all()
    t_lectures = [l for l in t_lectures if not l.id == lecture.id]

    conflicts = []    
    for t_lecture in t_lectures:
        for teacher in lecture.modulus.teachers:
            if teacher.id in [t.id for t in t_lecture.modulus.teachers]:
                conflicts.append((teacher, t_lecture))

    if not conflicts:
        print("Teachers are not conflicting.")
        return 0

    conflict_lectures = [c[1] for c in conflicts]

    message = ""
    for teacher, conflict_lecture in conflicts:
        cohort_code = conflict_lecture.modulus.cohort.code
        message += f"""O professor(a) {teacher.name} está ocupado(a) na turma {cohort_code}."""
        message += "<br>"

    if not lecture.joined_cohorts:
        final_message = "A aula que você está tentando agendar NÃO É conjunta. <br>"
        final_message += message
        flash(final_message, 'danger')
        return 1
    
    message = ""
    for teacher, conflict_lecture in [c for c in conflicts if not c[1].joined_cohorts]:
        cohort_code = conflict_lecture.modulus.cohort.code
        message += f"""O professor(a) {teacher.name} está ocupado(a) na turma {cohort_code}."""
        message += "<br>"

    if not all([l.joined_cohorts for l in conflict_lectures]):
        final_message = """A aula que você está tentando agendar é conjunta,
                           mas há aula(s) conflitantes que NÃO É(SÃO): <br>"""
        final_message += message
        flash(final_message, 'danger')
        return 1

    if not all([l.classroom_id == lecture.classroom_id for l in conflict_lectures]):
        final_message = """A aula que você está tentando agendar é conjunta,
                           mas há aula(s) conflitantes em salas diferentes: <br>"""
        for l in conflict_lectures:
            final_message += f"{l.classroom.name} <br>"
        flash(final_message, 'danger')
        return 1
    
    return 0


def check_prerequisites():
    # check if all prerequisites are being met
    pass


def check_for_intensive_classes(lecture):
    if not lecture.modulus.discipline.is_intensive:
        return 0

    date = lecture.date
    intensive_lectures = Lecture.check_intensive(date)
    intensive_lectures = [l for l in intensive_lectures if not l.modulus.id == lecture.modulus.id]
    intensive_lectures = [l for l in intensive_lectures if l.modulus.cohort.code == lecture.modulus.cohort.code]

    if not intensive_lectures:
        return 0
    
    conflict_name = intensive_lectures[0].modulus.discipline.name
    message = f"A disciplina é intensiva e já há aula(s) de {conflict_name} marcada(s) para o dia."
    flash(message, 'danger')
    return 1
    
    
