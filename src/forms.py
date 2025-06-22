from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=8)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[InputRequired(), EqualTo('password', message='Пароли должны совпадать')])

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=8)])

class OrderForm(FlaskForm):
    city = StringField('Город', validators=[InputRequired()])
    street = StringField('Улица', validators=[InputRequired()])
    apartment = StringField('Номер квартиры', validators=[InputRequired()])
    floor = IntegerField('Этаж', validators=[InputRequired()])
    delivery_time = StringField('Желаемое время доставки', validators=[InputRequired()])
    payment_method = SelectField('Способ оплаты', choices=[('При получении', 'При получении')], validators=[InputRequired()])