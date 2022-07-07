# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 17:35:39 2022

@author: Ernesto Cortés
"""

import sys
from flaskfantasy.models import Adp, Projections
from scrapers import *


season = int(sys.argv[1])
Apd.query.delete()
Projections.query.delete()
fantasypros_adp(season)
fantasypros_projections(season)
fantasyfootballcalc_adp(season)
