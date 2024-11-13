from flask import Blueprint, flash, redirect, render_template, url_for
from app.forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db


login_bp = Blueprint("login",
                     __name__,
                     template_folder="templates",
                     static_folder="static",
                     static_url_path="/static/login")


@login_bp.route("/")
def index():
    return redirect(url_for("login.login"))


@login_bp.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(name=form.name.data).first()

        if user and user.is_blocked and False:
            flash("Aguarde Liberação do Admin", 'danger')
            return redirect(url_for('login.login'))
        
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        
        if form.name.data and form.password.data:
            flash("Nome ou Senha Incorretos", 'danger')

    return render_template('login.html', title="Login", form=form, dont_show_logout=True)


@login_bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('login.login'))


@login_bp.route("/register", methods=["POST", "GET"])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flag = User.add_entry(form.name.data,
                              form.password.data)
        if flag == -2:
            flash("Nome já cadastrado", "danger")
            return redirect(url_for('login.register'))

        flash("Conta Criada Com Sucesso!", "success")
        return redirect(url_for('login.login'))
    else:
        print("not ok")

    return render_template('register.html', title="Register", form=form, dont_show_logout=True)
