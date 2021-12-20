from flask import Flask
import os
import redis
from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Configure Redis for storing the session data on the server-side
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url(os.environ.get('REDIS_URL'))
server_session = Session(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(user='postgres',
#                                                                                                   password='aeae1994',
#                                                                                                   host='localhost',
#                                                                                                   port='5432',
#                                                                                                   database='fantasy_football')
# db = SQLAlchemy(app)

from flaskfantasy import routes