from datetime import datetime

from flaskfantasy import db


class Adp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(10), nullable=False)
    team = db.Column(db.String(10))
    adp = db.Column(db.Float(2), nullable=False)
    scoring = db.Column(db.String(25), nullable=False)
    system = db.Column(db.String(25), nullable=False)
    season = db.Column(db.SmallInteger, nullable=False)
    source_name = db.Column(db.String(25), nullable=False)
    source_update = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    insert_timestamp = db.Column(db.DateTime, nullable=False) 
    
    def __repr__(self):
        return f"ADP('{self.player}', '{self.position}', '{self.scoring}', '{self.system}', '{self.season}', " \
               f"'{self.source_name}', '{self.source_update}')"


class Projections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(10), nullable=False)
    team = db.Column(db.String(10))
    pass_cmp = db.Column(db.Float(2), nullable=False)
    pass_att = db.Column(db.Float(2), nullable=False)
    pass_yd = db.Column(db.Float(2), nullable=False)
    pass_td = db.Column(db.Float(2), nullable=False)
    pass_int = db.Column(db.Float(2), nullable=False)
    rush_att = db.Column(db.Float(2), nullable=False)
    rush_yd = db.Column(db.Float(2), nullable=False)
    rush_td = db.Column(db.Float(2), nullable=False)
    receiv_rec = db.Column(db.Float(2), nullable=False)
    receiv_yd = db.Column(db.Float(2), nullable=False)
    receiv_td = db.Column(db.Float(2), nullable=False)
    fumble_lst = db.Column(db.Float(2), nullable=False)
    season = db.Column(db.SmallInteger, nullable=False)
    source_name = db.Column(db.String(25), nullable=False) 
    source_update = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    insert_timestamp = db.Column(db.DateTime, nullable=False) 
    
    def __repr__(self):
        return f"Projections('{self.player}', '{self.position}', '{self.season}', '{self.source_name}'," \
               f" '{self.source_update}')"
