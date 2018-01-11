from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Base model that for other models to inherit from
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Model for Restaurant
class Restaurant(Base):
    name = db.Column(db.String(200))
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True)
    def __repr__(self):
        return self.name

# Model for MenuItem
class MenuItem(Base):
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    name = db.Column(db.String(100))
    price = db.Column(db.String(10))
    description = db.Column(db.String(800))
    course = db.Column(db.String(800))
    def __repr__(self):
        return self.name
