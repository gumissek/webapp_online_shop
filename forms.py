from flask_wtf import FlaskForm
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.fields.simple import StringField, SubmitField, EmailField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length,Email,URL


class RegisterForm(FlaskForm):
    name = StringField(label='First name:',validators=[DataRequired()])
    surname = StringField(label='Surname:',validators=[DataRequired()])
    email = EmailField(label='E-mail:',validators=[DataRequired(),Email()])
    password = PasswordField(label='Password:',validators=[DataRequired(),EqualTo('retype_password',message='Password must match.'),Length(min=8,max=16,message='Password should contains 8-16 characters.')])
    retype_password = PasswordField(label='Repeat password:',validators=[DataRequired()])
    submit = SubmitField(label='Register')


class LoginForm(FlaskForm):
    email = EmailField(label='E-mail:',validators=[DataRequired(),Email()])
    password = PasswordField(label='Password:',validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class AddItemForm(FlaskForm):
    name = StringField(label='Item name',validators=[DataRequired()])
    description = TextAreaField(label='Item description',validators=[DataRequired()])
    category = StringField(label='Item category',validators=[DataRequired()])
    sub_category = StringField(label='Item subcategory',validators=[DataRequired()])
    price = FloatField(label='Item price',validators=[DataRequired(message='This field should contain a price')])
    img_link = StringField(label='Item img link',validators=[DataRequired()])
    EAN_code = IntegerField(label='EAN code',validators=[DataRequired()])
    manufacturer_code = StringField(label='Manufacturer code',validators=[DataRequired()])
    shop_code = IntegerField(label='Shop_code',validators=[DataRequired()])
    submit = SubmitField(label='Add item')