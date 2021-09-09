from flask import Flask
import os
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(user='postgres',
#                                                                                                   password='aeae1994',
#                                                                                                   host='localhost',
#                                                                                                   port='5432',
#                                                                                                   database='fantasy_football')
# db = SQLAlchemy(app)

from flaskfantasy import routes