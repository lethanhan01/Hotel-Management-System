from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm): 
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')

class RegisterForm(FlaskForm): 
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=100)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')