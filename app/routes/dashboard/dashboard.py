from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required

dashboard_bp = Blueprint(
                        'dashboard',
                        __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='/dashboard/static'
                        )
                        

@dashboard_bp.route('/dashboard/')
@login_required
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route('/delete-discipline/<discipline_code>')
@login_required
def delete_discipline(discipline_code):
    from app.models import Discipline
    discipline = Discipline.query.filter_by(code=discipline_code).first()
    discipline.delete_discipline()
    return f"discipline {discipline.name} deleted."

@dashboard_bp.route('/change-theoretical/<discipline_code>')
@login_required
def change_theoretical(discipline_code):
    from app.models import Discipline
    discipline = Discipline.query.filter_by(code=discipline_code).first()

    return discipline.change_theoretical()

@dashboard_bp.route('/change-intensive/<discipline_code>')
@login_required
def change_intensive(discipline_code):
    from app.models import Discipline
    discipline = Discipline.query.filter_by(code=discipline_code).first()

    return discipline.change_intensive()

@dashboard_bp.route('/change-workload/<discipline_code>/<new_workload>')
@login_required
def change_workload(discipline_code, new_workload):
    from app.models import Discipline
    discipline = Discipline.query.filter_by(code=discipline_code).first()
    return discipline.change_workload(new_workload)


@dashboard_bp.route('/delete-lectures/<discipline_code>')
@login_required
def delete_lectures(discipline_code):
    from app.models import Discipline
    discipline = Discipline.query.filter_by(code=discipline_code).first()
    return discipline.delete_lectures()


@dashboard_bp.route('/create-modulus/<discipline_code>/<cohort_code>')
@login_required
def create_modulus(discipline_code, cohort_code):
    from app.models import Modulus
    from app.models import Discipline
    from app.models import Cohort

    discipline = Discipline.query.filter_by(code=discipline_code).first()
    if not discipline:
        return f"Discipline {discipline_code} not found."
    cohort = Cohort.query.filter_by(code=cohort_code).first()
    if not cohort:
        return f"Cohort {cohort_code} not found."

    flag = Modulus.add_modulus(cohort.code, discipline.code)
    if isinstance(flag, Modulus):
        flag.set_main_classroom()

    return f"{flag}"


@dashboard_bp.route('/delete-modulus/<discipline_code>/<cohort_code>')
@login_required
def delete_modulus(discipline_code, cohort_code):
    from app.models import Modulus
    from app.models import Discipline
    from app.models import Cohort

    discipline = Discipline.query.filter_by(code=discipline_code).first()
    if not discipline:
        return f"Discipline {discipline_code} not found."
    cohort = Cohort.query.filter_by(code=cohort_code).first()
    if not cohort:
        return f"Cohort {cohort_code} not found."

    modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
    modulus.delete_modulus()
    return f"Modulus {discipline_code} from {cohort_code} deleted."


@dashboard_bp.route('/change-name/<discipline_code>/<new_name>/<new_abbr>')
@login_required
def change_name(discipline_code, new_name, new_abbr):
    from app.models import Discipline
    discipline = Discipline.query.filter_by(code=discipline_code).first()
    if not discipline:
        return f"Discipline {discipline_code} not found."
    
    flag = discipline.change_name(new_name, new_abbr)
    return f"{flag}"

@dashboard_bp.route('/find/<discipline_code>/<cohort_code>')
@login_required
def find_modulus(discipline_code, cohort_code):
    from app.models import Modulus
    from app.models import Discipline
    from app.models import Cohort

    discipline = Discipline.query.filter_by(code=discipline_code).first()
    if not discipline:
        return f"Discipline {discipline_code} not found."
    cohort = Cohort.query.filter_by(code=cohort_code).first()
    if not cohort:
        return f"Cohort {cohort_code} not found."

    modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
    if not modulus:
        return f"Modulus {discipline_code} from {cohort_code} not found."
    
    dates = list(set([l.date for l in modulus.lectures]))
    return dates


@dashboard_bp.route('/rm-teacher-disc/<discipline_code>/<teacher_name>')
@login_required
def remove_teacher_discipline(discipline_code, teacher_name):
    from app.models import Discipline, Teacher
    
    discipline = Discipline.query.filter_by(code=discipline_code).first()
    if not discipline:
        return f"Discipline {discipline_code} not found."
    
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return f"Teacher {teacher_name} not found."
    
    flag = discipline.remove_teacher(teacher.name)

    return f"{flag}"


@dashboard_bp.route('/rm-teacher-mod/<discipline_code>/<cohort_code>/<teacher_name>')
@login_required
def remove_teacher_modulus(discipline_code, cohort_code, teacher_name):
    from app.models import Discipline, Cohort, Modulus, Teacher
    
    discipline = Discipline.query.filter_by(code=discipline_code).first()
    if not discipline:
        return f"Discipline {discipline_code} not found."
    
    cohort = Cohort.query.filter_by(code=cohort_code).first()
    if not cohort:
        return f"Cohort {cohort_code} not found."
    
    teacher = Teacher.query.filter_by(name=teacher_name).first()
    if not teacher:
        return f"Teacher {teacher_name} not found."
    
    modulus = Modulus.query.filter_by(discipline_id=discipline.id, cohort_id=cohort.id).first()
    if not modulus:
        return f"Modulus {discipline_code} from {cohort_code} not found."
    
    flag = modulus.remove_teacher(teacher.name)

    return f"{flag}"
