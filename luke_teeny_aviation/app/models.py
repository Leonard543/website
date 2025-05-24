from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Airline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    aircraft = db.relationship('Aircraft', backref='airline', lazy=True)

    def __repr__(self):
        return f'<Airline {self.name}>'

class Aircraft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    airline_id = db.Column(db.Integer, db.ForeignKey('airline.id'), nullable=False)
    registrations = db.relationship('Registration', backref='aircraft', lazy=True)

    def __repr__(self):
        return f'<Aircraft {self.name}>'

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_code = db.Column(db.String, nullable=False, unique=True)
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircraft.id'), nullable=False)
    photo_filename = db.Column(db.String, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Registration {self.registration_code}>'
