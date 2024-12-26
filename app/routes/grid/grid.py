from flask import Blueprint, abort,  jsonify, redirect, render_template, make_response, url_for
from flask import request, current_app
import app.routes.grid.funcs as funcs
from app.models import Cohort, Classroom, Teacher
import app.global_vars as global_vars
from flask_weasyprint import HTML, CSS
from flask_login import login_required
import os

grid_bp = Blueprint(
                    'grid',
                    __name__,
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='/static/grid'
                    )


@grid_bp.route('/grid/', methods=['GET'])
@login_required
def grid_redirect():
    first_class_code = Cohort.query.all()[0].code
    return redirect(url_for('grid.grid', classCode=first_class_code, week=1))


@grid_bp.route('/grid/<classCode>/<week>', methods=['GET'])
@login_required
def grid(classCode, week):
    try:
        week = int(week)  # Ensure 'week' can be converted to an integer
    except ValueError:
        abort(400, description="Formato Inválido.")  # Bad request if not an integer

    if week < 1 or week > global_vars.NUM_WEEKS:
        abort(400, description="Semana não existe.")  # Bad request if out of range

    grid = funcs.gen_lectures_grid(classCode, week)

    cohort = Cohort.query.filter_by(code=classCode).first()
    if not cohort:
        abort(404, description="Turma não encontrada.")  # Not found if cohort does not exist

    if global_vars.ALTERNATING_WEEKS:
        parity = (week % 2 == 0) == cohort.theoretical_week_parity
        class_type = global_vars.TYPES_OF_CLASSES[parity]
        class_location = global_vars.LOCAL_OF_CLASSES[parity]
        get_all = False
    else:
        parity = None
        class_type = "TEÓRICAS E PRÁTICAS"
        class_location = "ESPC"
        get_all = True

    discipline_list = funcs.populate_discipline_list(classCode, parity, get_all=get_all)
    discipline_list_all = funcs.populate_discipline_list(classCode, parity, get_all=True)
    weeks = [i for i in range(1, global_vars.NUM_WEEKS+1)]
    cohorts = [c.code for c in Cohort.query.all()]
    message = f"{classCode} - AULAS {class_type} NA {class_location} - {week}ª SEMANA"
    classroom_list = ["-"] + [c.name for c in Classroom.query.all() if c.code not in ['0', '-1']]

    return render_template("grid.html",
                           grid=grid,
                           headerMessage=message,
                           toBeSelected=classCode,
                           select=cohorts,
                           timeUnit="Semana",
                           timeSelect=weeks,
                           currentTime=week,
                           disciplineList=discipline_list,
                           disciplineListAll=discipline_list_all,
                           classroomList=classroom_list,)


@grid_bp.route('/teachergrid/', methods=['GET'])
@login_required
def teachergrid_redirect():
    first_teacher_name = sorted([t.name for t in Teacher.query.all()])[0]
    first_month_num = global_vars.MONTHS[0]
    return redirect(url_for('grid.teacher_schedule', teacherName=first_teacher_name, month=first_month_num))


@grid_bp.route('/teachergrid/<teacherName>/<month>', methods=['GET'])
@login_required
def teacher_schedule(teacherName, month):
    months = global_vars.MONTHS
    month = int(month)
    grid = funcs.gen_teacher_schedule(teacherName, month)
    message = f"{teacherName} -- {month}ª MÊS"
    teachers = sorted([t.name for t in Teacher.query.all()])
    # str_month = list(global_vars.months_translation.values())[int(month)-1]

    return render_template("grid.html",
                           grid=grid,
                           headerMessage=message,
                           toBeSelected=teacherName,
                           select=teachers,
                           timeUnit="",
                           timeSelect=months,
                           currentTime=month,
                           disciplineList=[],
                           disciplineListAll=[],
                           classroomList=[],)


@grid_bp.route('/classroomgrid/', methods=['GET'])
@login_required
def classroomgrid_redirect():
    
    first_croom_name = [c.name for c in Classroom.query.all() if not (c.code == "-1" or c.code == "0")][0]
    return redirect(url_for('grid.classroom_schedule', classroomName=first_croom_name, week=1))


@grid_bp.route('/classroomgrid/<classroomName>/<week>', methods=['GET'])
@login_required
def classroom_schedule(classroomName, week):
    try:
        week = int(week)  # Ensure 'week' can be converted to an integer
    except ValueError:
        abort(400, description="Formato Inválido.")  # Bad request if not an integer

    if week < 1 or week > global_vars.NUM_WEEKS:
        abort(400, description="Semana não existe.")  # Bad request if out of range

    grid = funcs.gen_classroom_schedule(classroomName, week)
    
    message = f"{classroomName} -- {week}ª SEMANA"
    classrooms = [c.name for c in Classroom.query.all() if c.code not in ['0', '-1']]
    weeks = [i for i in range(1, global_vars.NUM_WEEKS+1)]

    return render_template("grid.html",
                           grid=grid,
                           headerMessage=message,
                           toBeSelected=classroomName,
                           select=classrooms,
                           timeUnit="Semana",
                           timeSelect=weeks,
                           currentTime=week,
                           disciplineList=[],
                           disciplineListAll=[],
                           classroomList=[],)


@grid_bp.route('/print/teachergrid/<teacherName>/<month>', methods=['GET'])
@login_required
def print_teachergrid(teacherName, month):
    try:
        month = int(month)  # Ensure 'month' can be converted to an integer
    except ValueError:
        abort(400, description="Formato Inválido.")

    # change to print_grid
    grid = funcs.gen_teacher_schedule(teacherName, month)

    teacher = Teacher.query.filter_by(name=teacherName).first()
    if not teacher:
        abort(404, description="Professor não encontrado.")
   
    # add check for mandatory classroom
    message = f"{teacherName} - {month}º MÊS"
    rendered = render_template("print_grid.html",
                                grid=grid,
                                message=message,)

    css_path = os.path.join(current_app.static_folder, 'css/colors.css')
    css = CSS(filename=css_path)

    pdf = HTML(string=rendered).write_pdf(stylesheets=[css], presentational_hints=True)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="print.pdf"'

    return response


@grid_bp.route('/print/grid/<classCode>/<week>', methods=['GET'])
@login_required
def print_grid(classCode, week):
    try:
        week = int(week)  # Ensure 'week' can be converted to an integer
    except ValueError:
        abort(400, description="Formato Inválido.")

    if week < 1 or week > global_vars.NUM_WEEKS:
        abort(400, description="Semana não existe.")

    # change to print_grid
    grid = funcs.gen_lectures_grid(classCode, week)

    cohort = Cohort.query.filter_by(code=classCode).first()
    if not cohort:
        abort(404, description="Turma não encontrada.")

    if global_vars.ALTERNATING_WEEKS:
        parity = (week % 2 == 0) == cohort.theoretical_week_parity
        class_type = global_vars.TYPES_OF_CLASSES[parity]
        class_location = global_vars.LOCAL_OF_CLASSES[parity]
    else:
        parity = None
        class_type = "TEÓRICAS E PRÁTICAS"
        class_location = "ESPC"
   
    # add check for mandatory classroom
    message = f"{classCode} - AULAS {class_type} NA {class_location} - {week}ª SEMANA"
    rendered = render_template("print_grid.html",
                                grid=grid,
                                message=message,)

    css_path = os.path.join(current_app.static_folder, 'css/colors.css')
    css = CSS(filename=css_path)

    pdf = HTML(string=rendered).write_pdf(stylesheets=[css], presentational_hints=True)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="print.pdf"'

    return response


@grid_bp.route('/update', methods=['POST'])
@login_required
def update_data():
    data = request.get_json()
    flag = funcs.resolve_lectures(data)

    if flag == 0:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error'})


@grid_bp.route('/matrix/', methods=['GET'])
@login_required
def matrix_redirect():
    return redirect(url_for('grid.matrix', parity=0, week=1))


@grid_bp.route('/matrix/<parity>/<week>', methods=['GET'])
@login_required
def matrix(parity, week):
    try:
        week = int(week)  # Ensure 'week' can be converted to an integer
    except ValueError:
        abort(400, description="Formato Inválido.")
    if week < 1 or week > global_vars.NUM_WEEKS:
        abort(400, description="Semana não existe.")
    
    grid = funcs.gen_matrix(parity, week)
    parities = [0, 1]
    weeks = [i for i in range(1, global_vars.NUM_WEEKS+1)]
    message = "matrix"

    return render_template("grid.html",
                            grid=grid,
                            headerMessage=message,
                            toBeSelected=parity,
                            select=parities,
                            timeUnit="Semana",
                            timeSelect=weeks,
                            currentTime=week,
                            disciplineList=[],
                            disciplineListAll=[],
                            classroomList=[],)