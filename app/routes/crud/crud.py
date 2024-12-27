from flask import Blueprint, request, render_template, redirect, url_for, jsonify, flash
from app.models import Modulus, Classroom, Teacher, Discipline, Cohort
import app.routes.grid.validation as validation
from flask_login import login_required
import app.routes.crud.funcs as funcs


crud_bp = Blueprint(
    'crud',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/crud'
)


@crud_bp.route('/crud/')
@login_required
def crud():
    return redirect(url_for('crud.add_teacher_to_modulus'))


@crud_bp.route('/crud/discipline', methods=['GET', 'POST'])
@login_required
def edit_discipline():
    areas = [{'id': 0, 'number': 'all'}] + [{'id':i, 'number':i} for i in range(1, 7)]
    all_disciplines = Discipline.query.all()

    all_disciplines = sorted(
        all_disciplines,
        key=lambda x: (
            float('.'.join(part.zfill(2) for part in x.code.replace('P', '').split('.'))),  # Pad fractions
            'P' in x.code  # Place 'P' codes after non-'P' codes
        )
    )
    return render_template('edit-discipline.html',
                            areas=areas,
                            initial_disciplines=all_disciplines)


@crud_bp.route('/crud/get_disciplines/<int:category_id>', methods=['GET'])
@login_required
def get_disciplines(category_id):
    return jsonify([])


@crud_bp.route('/crud/add-discipline/', methods=['GET', 'POST'])
@login_required
def add_discipline(): 
    if request.method == 'POST':
        print("TEST")
        name = request.form['name']
        name_abbr = request.form['name_abbr']
        code = request.form['code']
        workload = request.form['workload']
        # is_theoretical = request.form['is_theoretical'] == 'on'
        # is_intensive = request.form['is_intensive'] == 'on'
        # classroom = None if request.form['classroom'] == '0' else request.form['classroom']

        flag = Discipline.add_discipline(name,
                                         name_abbr,
                                         code,
                                         workload,
                                         True,
                                         False,
                                         mandatory_room=3,
                                        )

        flash(f'Classroom {flag.name} added successfully.', 'success')
        return redirect(url_for('dashboard.dashboard'))
    else:
        available_teachers = sorted(Teacher.query.all(), key=lambda x: x.name)
        
        return render_template('add-discipline.html',
                                available_teachers=available_teachers)


# @crud_bp.route('/crud/edit-discipline/', methods=['GET', 'POST'])
# @login_required
# def edit_discipline(): 
#     if request.method == 'POST':
#         name = request.form['name']
#         name_abbr = request.form['name_abbr']
#         code = request.form['code']
#         workload = request.form['workload']
#         is_theoretical = bool(request.form['is_theoretical'])
#         is_intensive = bool(request.form['is_intensive'])
#         classroom = None if request.form['classroom'] == '0' else request.form['classroom']



#         flag = Discipline.add_discipline(name,
#                                          name_abbr,
#                                          code,
#                                          workload,
#                                          is_theoretical,
#                                          is_intensive,
#                                          mandatory_room=classroom,
#                                         )

#         flash(f'Classroom {flag.name} added successfully.', 'success')
#         return redirect(url_for('dashboard.dashboard'))
#     else:
#         available_teachers = sorted(Teacher.query.all(), key=lambda x: x.name)
        
#         return render_template('edit-discipline.html')


@crud_bp.route('/crud/get-discipline/<discipline_code>')
@login_required
def get_discipline(discipline_code):
    discipline = Discipline.query.filter_by(code=discipline_code).first()
    # if discipline:
        # return jsonify(discipline.to_dict())
    test_dict = {
        'name': "nome",
        'code': "code",
        'workload': 10,
        'is_theoretical': True,
        'is_intensive': False
    }
    # return jsonify({'error': 'Discipline not found'}), 404
    return jsonify(test_dict)


@crud_bp.route('/crud/delete-discipline/<discipline_code>', methods=['POST'])
@login_required
def delete_discipline(discipline_code):
    print(discipline_code)

    return jsonify({})







@crud_bp.route('/crud/add-teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        abbr = request.form['abbr']
        rg = request.form['rg']
        flag = Teacher.add_teacher(name=name, abbr_name=abbr, rg=rg)
        if flag == 1:
            flash(f"The name {name} already part of the shabang", 'danger')
        elif flag == 2:
            flash(f"RG {rg} already part of the shabang", 'danger')
        else:
            flash(f'Teacher {name} added successfully.', 'success')

        return render_template('add-teacher.html')

    return render_template('add-teacher.html')


@crud_bp.route('/crud/add-teacher-discipline', methods=['GET', 'POST'])
@login_required
def add_teacher_to_discipline():
    discipline_teacher = [
        [f"{d.code}-{d.name} -- {d.teachers_names}: ", ""] for d in Discipline.query.all()]
    teachers = sorted([t.name for t in Teacher.query.all()])

    return render_template('crud-moduli.html',
                            pageName='Add Teacher to Discipline',
                            moduli=discipline_teacher,
                            options=teachers,
                            select_name='teacher',
                            request_path='add-teacher-discipline')


@crud_bp.route('/crud/rm-teacher-discipline', methods=['GET', 'POST'])
@login_required
def remove_teacher_from_discipline():
    discipline_teacher = [
        [f"{d.code}-{d.name} -- {d.teachers_names}: ", ""] for d in Discipline.query.all()]
    teachers = sorted([t.name for t in Teacher.query.all()])

    return render_template('crud-moduli.html',
                            pageName='Remove Teacher from Discipline',
                            moduli=discipline_teacher,
                            options=teachers,
                            select_name='teacher',
                            request_path='rm-teacher-discipline')


@crud_bp.route('/crud/add-teacher-moduli', methods=['GET', 'POST'])
@login_required
def add_teacher_to_modulus():
    moduli_teacher = [[f"{m.discipline.code}-{m.discipline.name} -- {m.code} -- {m.teachers_names}: ", ""] for m in Modulus.query.all()]
    teachers = sorted([t.name for t in Teacher.query.all()])

    return render_template('crud-moduli.html',
                            pageName='Add Teacher to Moduli',
                            moduli=moduli_teacher,
                            options=teachers,
                            select_name='teacher',
                            request_path='add-teacher-moduli')


@crud_bp.route('/crud/rm-teacher-moduli', methods=['GET', 'POST'])
@login_required
def remove_teacher_from_modulus():
    moduli_teacher = [[f"{m.discipline.code}-{m.discipline.name} -- {m.code} -- {m.teachers_names}: ", ""] for m in Modulus.query.all()]
    teachers = sorted([t.name for t in Teacher.query.all()])

    return render_template('crud-moduli.html',
                            pageName='Remove Teacher from Moduli',
                            moduli=moduli_teacher,
                            options=teachers,
                            select_name='teacher',
                            request_path='rm-teacher-moduli')


# Adding a classroom to modulus
@crud_bp.route('/crud/classroom', methods=['GET', 'POST'])
@login_required
def add_classroom_to_modulus():
    discipline_classroom = [[f"""{d.code} ~ {d.name} -- {"Externa" if d.is_theoretical else "Interna"}: """,
                             d.mandatory_room.name] for d in Discipline.query.all()]
    
    discipline_classroom = sorted(discipline_classroom, key=lambda x: x[1])
    classrooms = [c.name for c in Classroom.query.all()]

    return render_template('crud-moduli.html',
                            pageName='Add Classroom to Moduli',
                            moduli=discipline_classroom,
                            options=classrooms,
                            select_name='classroom',
                            request_path='classroom')

@crud_bp.route('/crud/add-classroom/', methods=['GET', 'POST'])
@login_required
def add_classroom():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        capacity = request.form['capacity']
        fungible = request.form['fungible']
        flag = Classroom.add_classroom(code, name, capacity, bool(fungible))
        if flag == 1:
            flash(f"Code {code} already part of the shabang", 'danger')
        elif flag == 2:
            flash(f"Name {name} already part of the shabang", 'danger')
        else:
            flash(f'Classroom {name} added successfully.', 'success')

        return render_template('add-classroom.html')

    return render_template('add-classroom.html')


@crud_bp.route('/crud/update', methods=['POST'])
@login_required
def crud_update():
    request_path = request.form.get('request_path')
    data = request.form
    if request_path in ['add-teacher-discipline', 'rm-teacher-discipline']:
        flag = funcs.resolve_teacher_to_discipline(data)
    elif request_path in ['add-teacher-moduli', 'rm-teacher-moduli']:
        flag = funcs.resolve_teacher_to_modulus(data)
    elif request_path == 'classroom':
        flag = funcs.resolve_classroom_to_modulus(data)
    else:
        return 'Invalid request path.'
    
    if flag:
        flash(flag, 'danger')

    return redirect(request_path)
