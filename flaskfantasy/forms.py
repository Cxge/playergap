from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField
from wtforms.validators import DataRequired

class SettingsForm(FlaskForm):
    scoring_format = SelectField('Scoring format', validators=[DataRequired()],
                                 choices=['PPR', 'Half-PPR', 'Non-PPR'],
                                 default='Half-PPR')
    
    num_teams = SelectField('Number of teams', validators=[DataRequired()],
                             choices=[8, 10, 12, 14],
                             default=12)
    
    roster_size = SelectField('Roster size', validators=[DataRequired()],
                              choices=[13, 14, 15, 16],
                              default=15)
    
    projections_source = SelectField('Fantasy points projections data source', validators=[DataRequired()],
                         choices=['FFToday'])
    
    adp_source = SelectField('ADP data source', validators=[DataRequired()],
                         choices=['FantasyFootballCalculator'])
    
    save_settings = SubmitField('Next')
    
class PlayerSelectionForm(FlaskForm):
    selection = StringField('Select player', validators=[DataRequired()], render_kw={'autofocus':True})
    
    submit_selection = SubmitField('Submit')
    
class BeginForm(FlaskForm):
    begin = SubmitField('BEGIN')
