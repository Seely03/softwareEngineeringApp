from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp
from app.models import User, Ticket, Project
from wtforms import validators

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    is_admin = BooleanField('Create as Admin')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TicketForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Closed', 'Closed')])
    submit = SubmitField('Submit')

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')

    def validate_name(self, name):
        project = Project.query.filter_by(name=name.data).first()
        if project:
            raise ValidationError('A project with that name already exists.')

class AssignUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Assign User')

class EmptyForm(FlaskForm):
    pass
