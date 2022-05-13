from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SelectField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email


class SettingsForm(FlaskForm):
    system = SelectField('System',
                         validators=[DataRequired()],
                         choices=['1-QB', '2-QB', 'Dynasty', 'Rookie'],
                         default='1-QB')
    
    scoring_format = SelectField('Scoring format',
                                 validators=[DataRequired()],
                                 choices=['PPR', 'Half-PPR', 'Non-PPR'],
                                 default='Half-PPR')
    
    num_teams = SelectField('Number of teams',
                            validators=[DataRequired()],
                            choices=[8, 10, 12, 14, 16],
                            default=12)
    
    roster_size = SelectField('Roster size',
                              validators=[DataRequired()],
                              choices=[i for i in range(10, 17)],
                              default=13)
    
    projections_source = SelectField('FPts projections data source',
                                     validators=[DataRequired()],
                                     choices=[])
    
    adp_source = SelectField('ADP source',
                             validators=[DataRequired()],
                             choices=[])
    
    save_settings = SubmitField('Next')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    subject = StringField('Subject', validators=[DataRequired()])
    
    message = TextAreaField('Message', validators=[DataRequired()])

    recaptcha = RecaptchaField()
    
    send = SubmitField('Send')
