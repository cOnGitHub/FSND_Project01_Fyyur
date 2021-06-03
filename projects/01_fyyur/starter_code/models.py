from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db = SQLAlchemy(app)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=True)
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

  # I used Udacity Knowledge to understand how to implement genres: 
  # https://knowledge.udacity.com/questions/63411
  genres = db.Column(db.ARRAY(db.String), nullable=False) #db.PickleType, nullable=False
  website_link = db.Column(db.String(120), nullable=True)
  seeking_talent = db.Column(db.Boolean(), nullable=True, default=False)
  seeking_description = db.Column(db.String(120), nullable=True)
  shows = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=True)
  # I used Udacity Knowledge to understand how to implement genres: 
  # https://knowledge.udacity.com/questions/63411
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

  website_link = db.Column(db.String(120), nullable=True)
  seeking_venue = db.Column(db.Boolean(), nullable=True, default=False)
  seeking_description = db.Column(db.String(120), nullable=True)
  shows = db.relationship('Show', backref='artist', lazy=True)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

