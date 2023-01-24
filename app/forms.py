from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class UserRegistrationForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    phone_number = StringField('Номер телефона', validators=[DataRequired(), Length(min=11, max=12)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4, max=80)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_phone_number(self, phone_number):
        user = User.query.filter(User.phone_number==phone_number.data).first()
        if user:
            raise ValidationError('Этот номер уже занят, попробуйте другой')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Аккаунт с данной почтой уже существует!')

        

class UserUpdateForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    phone_number = StringField('Номер телефона', validators=[DataRequired(), Length(min=11, max=12)])
    update = SubmitField('Обновить')


class LoginForm(FlaskForm):
    email = StringField('Электронная почта', validators=[
                        DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[
                             DataRequired(), Length(min=4, max=80)])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class ResetForm(FlaskForm):
    email = StringField('Электронная почта', validators=[
                        DataRequired(), Email()])
    submit = SubmitField('Сбросить пароль')

class SetPasswordForm(FlaskForm):
    email = StringField('Электронная почта', validators=[
                        DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[
                             DataRequired(), Length(min=4, max=80)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сбросить пароль')
