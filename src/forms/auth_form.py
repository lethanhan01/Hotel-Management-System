from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm): 
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=100)])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember_me = BooleanField('Nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

class RegisterForm(FlaskForm): 
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=100)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng ký')