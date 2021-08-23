from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '7e44d6bd92b4c4bcf35010db0b9d0e65' #FALTA CONVERTIRLA A VARIABLE DE ENTORNO
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{password}@{host}:{port}/{database}'.format(user='postgres',
#                                                                                                   password='aeae1994',
#                                                                                                   host='localhost',
#                                                                                                   port='5432',
#                                                                                                   database='fantasy_football')
# db = SQLAlchemy(app)

from flaskfantasy import routes