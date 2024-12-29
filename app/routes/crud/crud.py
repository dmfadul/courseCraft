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
    areas = [{'id': 1000, 'number': 'all'}] + [{'id':i, 'number':i} for i in range(7)]
    all_disciplines = Discipline.query.all()

    all_disciplines = Discipline.sort_by_code(all_disciplines)

    return render_template('edit-discipline.html',
                            areas=areas,
                            initial_disciplines=all_disciplines)


@crud_bp.route('/crud/get_disciplines/<int:class_code>', methods=['GET'])
@login_required
def get_disciplines(class_code):
    if class_code == 1000:
        disciplines = [d for d in Discipline.query.all()]
    else:
        disciplines = [d for d in Discipline.query.all() if d.code.startswith(str(class_code))]
    
    disciplines = Discipline.sort_by_code(disciplines)

    return jsonify([d.to_dict() for d in disciplines])


@crud_bp.route('/crud/get_discipline_info/<int:discipline_id>', methods=['GET'])
@login_required
def get_discipline_info(discipline_id):
    discipline = Discipline.query.filter_by(id=discipline_id).first()
    if not discipline:
        return jsonify({'error': 'Discipline not found'}), 404
    
    modules = discipline.moduli
    modules_dict = [m.to_dict() for m in modules]

    teachers_names = [(0, '-')] 
    teachers_names += [(t.id, t.name) for t in sorted(Teacher.query.all(), key=lambda x: x.name)]

    classrooms = [(0, '-')]
    classrooms += [(c.id, c.name) for c in sorted(Classroom.query.all(), key=lambda x: x.name)]

    data_dict = {"discipline": discipline.to_dict(),
                 "modules": modules_dict,
                 "teachersNames": teachers_names,
                 "classrooms": classrooms,}

    return jsonify(data_dict)


@crud_bp.route('/crud/update_discipline', methods=['POST'])
@login_required
def update_discipline():
    data = request.get_json()
    print("data", data)

    return jsonify({'response': 'ok'})


@crud_bp.route('/crud/delete-discipline/<discipline_code>', methods=['POST'])
@login_required
def delete_discipline(discipline_code):
    print(discipline_code)

    return jsonify({'response': 'ok'})


@crud_bp.route('/crud/delete-module', methods=['POST'])
@login_required
def delete_modulus():
    data = request.get_json()
    code = data['code']
    print(code)

    return jsonify({'response': 'ok'})








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
