from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NoneOf
from flaskRecommender.models import User

'''
setting the form in the application 
'''
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    gender = SelectField('Gender', choices=[('NA', ''), ('M', 'Male'), ('F', 'Female')], validators=[DataRequired(), NoneOf(['NA'])])
    age = SelectField('Age', choices=[(0, ''), (1, "Under 18"), (18, '18-24'), (25, '25-34'), (35, '35-44'), (45, '45-49'), (50, '50-55'), ('56', '56+')], coerce=int, validators=[DataRequired(), NoneOf([0])])
    occupation = SelectField('Occupation', choices=[(-1, ''), (0, 'other'), (1, 'academic/educator'), (2, 'artist'),
 (3, 'clerical/admin'), (4, 'college/grad student'), (5, 'customer service'), (6, 'doctor/health care'),
 (7, 'executive/managerial'), (8, 'farmer'), (9, 'homemaker'), (10, 'K-12 student'), (11, 'lawyer'),
 (12, 'programmer'), (13, 'retired'), (14, 'sales/marketing'), (15, 'scientist'), (16, 'self-employed'),
 (17, 'technician/engineer'), (18, 'tradesman/craftsman'), (19, 'unemployed'), (20, 'writer')], coerce=int,
                             validators=[DataRequired(), NoneOf([-1])])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is registered, please try to sign in')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RatingForm(FlaskForm):
    movieID = StringField('MovieID')
    yes = SubmitField('Yes')
    no = SubmitField('No')
    moderate = SubmitField('Moderate')
    unknown = SubmitField('I don\'t know this movie')


