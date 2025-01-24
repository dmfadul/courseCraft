from flask import Blueprint, render_template
import app.routes.reports.funcs as funcs
from flask_login import login_required

reports_bp = Blueprint(
                       'reports',
                       __name__,
                       template_folder='templates',
                       static_folder='static',
                       static_url_path='/static/reports'
                       )

REPORTS_DICT = {
    'Carga Horária dos Professores': funcs.calculate_teachers_workload,
    'Checar Matérias sem Professores': funcs.check_classes_for_teachers,
    'Checar Aulas sem Sala': funcs.check_classes_for_classrooms,
    'Checar Conflitos de Sala': funcs.check_for_classroom_conflicts,
    'Checar Disciplinas Físicas': funcs.check_proximity_of_intensive_moduli,
    'Checar Prerequisitos': funcs.check_prerequisites,
    'Checar Aulas Fora de Salas Obrigatórias': funcs.check_lectures_in_odd_classrooms,
    'Checar Aulas na Semana Errada': funcs.check_lectures_in_wrong_week,
    'Checar Conflitos de Professores': funcs.check_teachers_conflicts,
    'Listar Professores Por Turma': funcs.list_teachers_by_cohorts,
    }


@reports_bp.route('/reports/', methods=['GET'])
@login_required
def reports():
    reports_list = ["-"] + list(REPORTS_DICT.keys())
    return render_template("reports.html", reportsList=reports_list)


@reports_bp.route('/fetch_report/<report_name>')
@login_required
def fetch_report(report_name):

    data = REPORTS_DICT.get(report_name, None)()
    if data:
        return render_template('report_template.html', grid=data, report_name=report_name)
    else:
        return '<p>Report not found</p>', 404
