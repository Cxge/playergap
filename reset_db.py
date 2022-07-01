# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 17:35:39 2022

@author: Ernesto Cortés
"""

from flaskfantasy import db
from scrapers import *

db.drop_all()
db.create_all()
fantasypros_adp(2022)
fantasypros_projections(2022)
fantasyfootballcalc_adp(2022)