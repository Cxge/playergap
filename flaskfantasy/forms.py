from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email

class SettingsForm(FlaskForm):
    scoring_format = SelectField('Scoring format', validators=[DataRequired()],
                                 choices=['PPR', 'Half-PPR', 'Non-PPR'],
                                 default='Half-PPR')
    
    num_teams = SelectField('Number of teams', validators=[DataRequired()],
                             choices=[8, 10, 12, 14, 16],
                             default=12)
    
    roster_size = SelectField('Roster size', validators=[DataRequired()],
                              choices=[13, 14, 15, 16],
                              default=15)
    
    projections_source = SelectField('Fantasy points projections data source', validators=[DataRequired()],
                         choices=['FFToday'])
    
    adp_source = SelectField('ADP data source', validators=[DataRequired()],
                         choices=['FantasyFootballCalculator'])
    
    save_settings = SubmitField('Next')
       
class BeginForm(FlaskForm):
    begin = SubmitField('BEGIN')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    subject = StringField('Subject', validators=[DataRequired()])
    
    message = TextAreaField('Message', validators=[DataRequired()])
    
    send = SubmitField('SEND')
