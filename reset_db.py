# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 17:35:39 2022

@author: Ernesto Cortés
"""

import sys
from flaskfantasy import db
from scrapers import *


season = int(sys.argv[1])
db.drop_all()
db.create_all()
fantasypros_adp(season)
fantasypros_projections(season)
fantasyfootballcalc_adp(season)
