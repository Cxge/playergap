from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SelectField, SubmitField, StringField, TextAreaField, DecimalField, BooleanField
from wtforms.validators import InputRequired


class SettingsForm(FlaskForm):
    system = SelectField('System',
                         validators=[InputRequired()],
                         choices=['1-QB', '2-QB', 'Dynasty', 'Rookie'],
                         default='1-QB')
    
    scoring_format = SelectField('Scoring format',
                                 validators=[InputRequired()],
                                 choices=['PPR', 'Half-PPR', 'Non-PPR'],
                                 default='Half-PPR')

    projections_source = SelectField('FPts projections data source',
                                     validators=[InputRequired()],
                                     choices=[])
    
    adp_source = SelectField('ADP source',
                             validators=[InputRequired()],
                             choices=[])
    
    num_teams = SelectField('Number of teams',
                            validators=[InputRequired()],
                            choices=[8, 10, 12, 14, 16, 18, 20],
                            default=12)
    
    roster_size = SelectField('Roster size',
                              validators=[InputRequired()],
                              choices=[*range(12, 19)],
                              default=15)

    kickers_flag = BooleanField('Kickers', default="checked")

    defenses_flag = BooleanField('Defenses', default="checked")

    keepers_flag = BooleanField('Keepers')

    pass_yd = DecimalField('Passing yards',
                            validators=[InputRequired()],
                            default=25,
                            places=0)

    pass_td = DecimalField('Passing touchdown',
                            validators=[InputRequired()],
                            default=4,
                            places=0)

    pass_int = DecimalField('Interception thrown',
                            validators=[InputRequired()],
                            default=-2,
                            places=0)

    rush_yd = DecimalField('Rushing yards',
                            validators=[InputRequired()],
                            default=10,
                            places=0)

    rush_td = DecimalField('Rushing touchdown',
                            validators=[InputRequired()],
                            default=6,
                            places=0)

    receiv_yd = DecimalField('Receiving yards',
                            validators=[InputRequired()],
                            default=10,
                            places=0)

    receiv_td = DecimalField('Receiving touchdown',
                            validators=[InputRequired()],
                            default=6,
                            places=0)

    fumble_lst = DecimalField('Fumble lost',
                            validators=[InputRequired()],
                            default=-2,
                            places=0)

    field_goal = DecimalField('Field goal',
                            validators=[InputRequired()],
                            default=3,
                            places=0)

    extra_pt = DecimalField('Extra point',
                            validators=[InputRequired()],
                            default=1,
                            places=0)

    sack = DecimalField('Sack',
                            validators=[InputRequired()],
                            default=1,
                            places=0)

    interception = DecimalField('Interception',
                            validators=[InputRequired()],
                            default=2,
                            places=0) 

    fumble_recovered = DecimalField('Fumble recovered',
                            validators=[InputRequired()],
                            default=2,
                            places=0) 

    def_td = DecimalField('Touchdown',
                            validators=[InputRequired()],
                            default=6,
                            places=0)

    safety = DecimalField('Safety',
                            validators=[InputRequired()],
                            default=2,
                            places=0)
    
    save_settings = SubmitField('Next')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    
    email = StringField('Email', validators=[InputRequired()])
    
    subject = StringField('Subject', validators=[InputRequired()])
    
    message = TextAreaField('Message', validators=[InputRequired()])

    recaptcha = RecaptchaField()
    
    send = SubmitField('Send')
