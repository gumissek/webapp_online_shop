from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField(label='First name:',validators=[DataRequired()])
    surname = StringField(label='Surname:',validators=[DataRequired()])
    email = EmailField(label='E-mail:',validators=[DataRequired()])
    password = PasswordField(label='Password:',validators=[DataRequired()])
    retype_password = PasswordField(label='Retype password:',validators=[DataRequired()])
    submit = SubmitField(label='Register')


class LoginForm(FlaskForm):
    email = EmailField(label='E-mail:',validators=[DataRequired()])
    password = PasswordField(label='Password:',validators=[DataRequired()])
    submit = SubmitField(label='Sign in')