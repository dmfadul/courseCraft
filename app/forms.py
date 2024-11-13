from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(2, 15)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(3, 20)])
    remember = BooleanField('Lembre-se de Mim')

    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(2, 15)])

    password = PasswordField('Senha', validators=[DataRequired(), Length(3, 20)])
    confirm_password = PasswordField('Confirme a Senha', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Confirmar')
