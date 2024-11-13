from app.models import Discipline, Teacher, Cohort, Modulus, Classroom
import app.routes.grid.validation as validation
from flask import flash


def resolve_teacher_to_modulus(data):
    request_path = data.get('request_path')
    discipline_code = data.get('discipline').split('-')[0].strip()
    modulus_code = data.get('discipline').split(' -- ')[1].strip()

    teacher_name = data.get('teacher')
    cohort_code = modulus_code.split('-')[1].strip()

    discipline = Discipline.query.filter_by(code=discipline_code).first()
    if not discipline:
        return 'Discipline not found.'

    cohort = Cohort.query.filter_by(code=cohort_code).first()
    if not cohort:
        return 'Cohort not found.'

    modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
    if not modulus:
        return 'Modulus not found.'

    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return 'Teacher not found.'
    
    if request_path == 'add-teacher-modulus':
        if teacher in modulus.teachers:
            return f"{teacher_name} is already a part of {modulus.code}-{modulus.discipline.name}."
        
        if not teacher in discipline.teachers:
            discipline.add_teacher(teacher_name)

        flag = validation.check_teacher_conflicts(teacher, modulus)
        if flag:
            return flag

        message = modulus.add_teacher(teacher.name)
        if message:
            flash(message, 'danger')
        return 0
    else:
        if not teacher in modulus.teachers:
            return f"O professor(a) {teacher_name} não está vinculado(a) à disciplina {modulus.code}."
        
        message = modulus.remove_teacher(teacher_name)
        if message:
            flash(message, 'danger')
        return 0


def resolve_teacher_to_discipline(data):
    request_path = data.get('request_path')
    discipline_code = data.get('discipline').split('-')[0].strip()
    teacher_name = data.get('teacher')

    discipline = Discipline.query.filter_by(code=discipline_code).first()
    if not discipline:
        return 'Discipline not found.'

    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return 'Teacher not found.'

    if request_path == 'add-teacher-discipline':
        if teacher in discipline.teachers:
            return f"{teacher_name} is already a part of {discipline.code}-{discipline.name}."

        message = discipline.add_teacher(teacher.name)
        if message:
            flash(message, 'danger')

        return 0
    else:
        if not teacher in discipline.teachers:
            return f"O professor(a) {teacher_name} não está vinculado(a) à disciplina {discipline.name}."

        message = discipline.remove_teacher(teacher_name)
        if message:
            flash(message, 'danger')

        return 0
    
def resolve_classroom_to_modulus(data):
    new_classroom_name = data.get('classroom')
    new_classroom = Classroom.query.filter_by(name=new_classroom_name).first()
    
    discipline_code = data.get('discipline').split('~')[0].strip()
    discipline = Discipline.query.filter_by(code=discipline_code).first()
    discipline.add_mandatory_room(new_classroom.code)

    for modulus in discipline.moduli:
        modulus.remove_main_classroom()
        modulus.set_main_classroom()

    return 0



    # flag = validation.check_classroom_availability(classroom, modulus)
    # if flag:
    #     flash(flag, 'danger')
    #     return 0

    # message = modulus.force_main_classroom(classroom.name)
    # if message:
    #     flash(message, 'danger')
    #     return 0
