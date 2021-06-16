from app import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(64))
    balance_rubles = db.Column(db.Float)
    balance_dollars = db.Column(db.Float)
    gold_mine = db.relationship("GoldMine", backref="users", lazy=True, uselist=False)
    menu = db.Column(db.String(64))


class GoldMine(db.Model):
    __tablename__ = "goldmines"
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    diggers = db.relationship("Digger", backref="goldmines", lazy=True)


class Digger(db.Model):
    __tablename__ = "diggers"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64))
    income = db.Column(db.Integer)
    price = db.Column(db.Integer)
    gold_mine_id = db.Column(db.Integer, db.ForeignKey("goldmines.id"))
    count = db.Column(db.Integer)
