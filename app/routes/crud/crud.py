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


@crud_bp.route('/crud/add-discipline/', methods=['GET', 'POST'])
@login_required
def add_discipline():
    if request.method == 'POST':
        name = request.form['name']
        abbr = request.form['abbr']
        code = request.form['code']
        workload = request.form['workload']
        cohorts_str = request.form['cohorts']

        code_check = Discipline.query.filter_by(code=code).first()
        if code_check is not None:
            flash(f"Code {code} already part of the shabang", 'danger')
            return redirect(url_for('crud.add_discipline'))

        name_check = Discipline.query.filter_by(name=name).first()
        if name_check is not None:
            flash(f"Name {name} already part of the shabang", 'danger')
            return redirect(url_for('crud.add_discipline'))

        new_disc = Discipline.add_discipline(name=name,
                                         name_abbr=abbr,
                                         code=code,
                                         workload=int(workload),
                                         is_theoretical=True,
                                         is_intensive=False)
        
        if not isinstance(new_disc, Discipline):
            flash("an Error has ocurred", 'danger')
            return redirect(url_for('crud.add_discipline'))

        cohorts_list = cohorts_str.split('+')
        cohorts = Cohort.query.all()
        for cohort in cohorts:
            code = cohort.code
            code_base = ''.join([l for l in code if not l.isdigit()])
            if code_base not in cohorts_list:
                continue

            flag = Modulus.add_modulus(cohort.code, new_disc.code)
            if isinstance(flag, Modulus):
                flag.set_main_classroom()
        
        flash(f'Discipline {name} added successfully.', 'success')
        return redirect(url_for('crud.add_discipline'))
    
    return render_template('add-discipline.html')


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


@crud_bp.route('/crud/add-user', methods=['GET', 'POST'])
@login_required
def add_user():
    from app.models import User
    if request.method == 'POST':
        user_name = request.form['userName']
        password =  request.form['password']
        confirmation =  request.form['confirmation']

        if password != confirmation:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('crud.add_user'))

        flag = User.add_entry(user_name, password)
        if isinstance(flag, str):
            flash(flag, 'danger')
            return redirect(url_for('crud.add_user'))

        flash('User created', 'success')
        return redirect(url_for('crud.add_user'))

    return render_template('add-users.html')



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
    from app.routes.grid.validation import check_conflicting_classrooms
    from app.routes.grid.validation import check_teachers_availability
    from app.routes.grid.validation import check_for_intensive_classes

    data = request.get_json()
    
    disc_code = data['disciplineSummary']['code']
    discipline = Discipline.query.filter_by(code=disc_code).first()

    if not discipline:
        return jsonify({'error': 'Discipline not found'}), 404
    
    new_abbr = data['disciplineSummary']['abbreviation']
    new_name = data['disciplineSummary']['name']
    new_workload = data['disciplineSummary']['workLoad']
    
    if not discipline.name == new_name or not discipline.name_abbr == new_abbr:
        discipline.change_name(new_name, new_abbr)

    if not discipline.workload == new_workload:
        discipline.change_workload(new_workload)

    mod_data = data['modules']
    for datum in mod_data:
        mod_code = datum['code']
        moduli = [m for m in discipline.moduli if m.code == mod_code]

        if not len(moduli) == 1:
            return jsonify({'error': 'Module not found'}), 404
        
        modulus = moduli[0]

        old_teachers = modulus.teachers.copy()
        old_teachers_ids = sorted([t.id for t in old_teachers])
        new_teachers_ids = sorted([int(t) for t in datum['teachers'] if t != '0'])

        if not old_teachers_ids == new_teachers_ids:
            new_teachers = []
            for teacher_id in new_teachers_ids:
                teacher = Teacher.query.filter_by(id=teacher_id).first()
                if not teacher:
                    return jsonify({'error': 'Teacher not found'}), 404
                new_teachers.append(teacher)

            modulus.replace_teachers(new_teachers)

        for lec in modulus.lectures:
            teacher_flag = check_teachers_availability(lec)
            if teacher_flag:
                modulus.replace_teachers(old_teachers)
                return jsonify({
                    'error': "Um dos professores incluídos tem aulas em conflito com as desta disciplina",
                    'message': "Um dos professores incluídos tem aulas em conflito com as desta disciplina"  # Include the detailed flag message
                }), 400
            
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
