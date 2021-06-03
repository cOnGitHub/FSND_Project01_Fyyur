#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import numpy as np
from models import Venue, Artist, Show, db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# I found this Udacity knowledge article helpful on migrating models to models.py
# https://knowledge.udacity.com/questions/282547
db.init_app(app) #SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI'] #'postgresql://postgres:admin@localhost:5432/fyyurapp'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# See file modely.py

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []

  try:
    city_states = db.session.query(Venue.city, Venue.state).all()
    # See here on how to get unique tuples:
    # https://stackoverflow.com/questions/35975441/grab-unique-tuples-in-python-list-irrespective-of-order
    city_states = np.unique(city_states, axis=0)
    #flash(type(city_states))

    for city, state in city_states:
      city_state = {}
      city_state['city'] = city
      city_state['state'] = state

      city_state_venues = []

      for v in Venue.query.filter_by(city=city, state=state).all():
        venue_dict = {}
        venue_dict['id'] = v.id
        venue_dict['name'] = v.name
        venue_dict['num_upcoming_shows'] = Show.query.filter_by(venue_id=v.id).filter(Show.start_time < datetime.now()).count()
        city_state_venues.append(venue_dict)

      city_state['venues'] = city_state_venues
      data.append(city_state)
    
    #flash(data)
    return render_template('pages/venues.html', areas=data)

  except:
    return render_template('errors/500.html')

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  # return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  response = {}
  search_term = request.form.get('search_term')

  search_results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

  response['count'] = len(search_results)
  response['data'] = []

  for result in search_results:
    venue = {}
    venue['id'] = result.id
    venue['name'] = result.name
    venue['num_upcoming_shows'] = Show.query.filter_by(venue_id=result.id).filter(Show.start_time > datetime.now()).count()
    response['data'].append(venue)
  
  #flash(response)
  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  try:
    venue = Venue.query.get(venue_id)
    #flash(venue)
    # See the discussion here on how to convert an object of type Module into a dict:
    # https://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
    data = {col.name: getattr(venue, col.name) for col in venue.__table__.columns}
    #flash(data)

    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []

    for show in shows:
      show_data = {}
      artist = Artist.query.get(show.artist_id)

      # flash(show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
      show_data['artist_id'] = artist.id
      show_data['artist_name'] = artist.name
      show_data['artist_image_link'] = artist.image_link
      show_data['start_time'] = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
      if show.start_time < datetime.now():
        past_shows.append(show_data)
      else:
        upcoming_shows.append(show_data)
        
    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = len(upcoming_shows)
      
    return render_template('pages/show_venue.html', venue=data)
  
  except:
    return render_template('errors/500.html')

  #flash(data)

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  # return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  # I used the information about the CSRF token from this Udacity Knowledge Post:
  # https://knowledge.udacity.com/questions/536070 
  form = VenueForm(request.form, meta={'csrf': False})

  if form.validate_on_submit():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      image_link = request.form['image_link']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      website_link = request.form['website_link']
      # I got the idea on how to implement seeking_talent in this Udacity Knowledge post:
      # https://knowledge.udacity.com/questions/75010
      if ('seeking_talent' in request.form):
        seeking_talent = (request.form['seeking_talent']=='y')
      else:
        seeking_talent = False
      seeking_description = request.form['seeking_description']
      
      venue = Venue(name=name, city=city, state=state, address=address,
      phone=phone, image_link=image_link, genres=genres, 
      facebook_link=facebook_link, website_link=website_link,
      seeking_talent=seeking_talent, seeking_description=seeking_description)

      db.session.add(venue)
      db.session.commit()

    except:
      error = True
      #flash(sys.exc_info())
      db.session.rollback()
    
    finally:
      db.session.close()
      
    if not error:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    if error: 
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be created')

    return render_template('pages/home.html')
  else:
    flash('You have Errors: ')
    for field, err in form.errors.items():
      flash(''.join(field).replace('_', ' ').title() + ' : \'' + ''.join(err) + '\'' )
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = []

  try:
    artists = Artist.query.all()

    for item in artists:
      artist = {}
      artist['id'] = item.id
      artist['name'] = item.name

      data.append(artist)
    
    #flash(data)
    return render_template('pages/artists.html', artists=data)

  except:
    return render_template('errors/500.html')

  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  # return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  search_term = request.form.get('search_term')

  search_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  response['count'] = len(search_results)
  response['data'] = []

  for result in search_results:
    artist = {}
    artist['id'] = result.id
    artist['name'] = result.name
    artist['num_upcoming_shows'] = Show.query.filter_by(artist_id=result.id).filter(Show.start_time > datetime.now()).count()
    response['data'].append(artist)
  
  #flash(response)
  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  try:
    artist = Artist.query.get(artist_id)
    #flash(artist)
    data = {col.name: getattr(artist, col.name) for col in artist.__table__.columns}
    #flash(data)

    shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = []
    upcoming_shows = []

    for show in shows:
      show_data = {}
      venue = Venue.query.get(show.venue_id)

      # flash(show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
      show_data['venue_id'] = venue.id
      show_data['venue_name'] = venue.name
      show_data['venue_image_link'] = venue.image_link
      show_data['start_time'] = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
      if show.start_time < datetime.now():
        past_shows.append(show_data)
      else:
        upcoming_shows.append(show_data)
        
    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = len(upcoming_shows)
      
    return render_template('pages/show_artist.html', artist=data)
  
  except:
    return render_template('errors/500.html')
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  # return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  # I consulted this Udacity Knowledge article in order to solve this task:
  # https://knowledge.udacity.com/questions/250457

  result = Artist.query.get(artist_id)
  form = ArtistForm(obj=result)

  artist = {col.name: getattr(result, col.name) for col in result.__table__.columns}
  #flash(artist)

  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  form = ArtistForm(request.form, meta={'csrf': False})
  a = Artist.query.get(artist_id)


  if form.validate_on_submit():

    try:
      a.name = request.form['name']
      a.city = request.form['city']
      a.state = request.form['state']
      a.phone = request.form['phone']
      a.image_link = request.form['image_link']
      a.genres = request.form.getlist('genres')
      a.facebook_link = request.form['facebook_link']
      a.website_link = request.form['website_link']
      #flash(a.website_link)

      if ('seeking_venue' in request.form):
        a.seeking_venue = (request.form['seeking_venue']=='y')
      else:
        a.seeking_venue = False

      a.seeking_description = request.form['seeking_description']
      
      db.session.commit()

    except:
      error = True
      #flash(sys.exc_info())
      db.session.rollback()
    
    finally:
      db.session.close()
      
    if not error:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')

    if error: 
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated')

    return redirect(url_for('show_artist', artist_id=artist_id))

  else:
    flash('You have Errors: ')
    for field, err in form.errors.items():
      flash(''.join(field).replace('_', ' ').title() + ' : \'' + ''.join(err) + '\'' )
    return render_template('forms/edit_artist.html', form=form, artist=a)
            

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  result = Venue.query.get(venue_id)
  form = VenueForm(obj=result)

  venue = {col.name: getattr(result, col.name) for col in result.__table__.columns}
  #flash(venue)

  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  v = Venue.query.get(venue_id)

  if form.validate_on_submit():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
      v.name = request.form['name']
      v.city = request.form['city']
      v.state = request.form['state']
      v.address = request.form['address']
      v.phone = request.form['phone']
      v.image_link = request.form['image_link']
      v.genres = request.form.getlist('genres')
      v.facebook_link = request.form['facebook_link']
      v.website_link = request.form['website_link']
      # I got the idea on how to implement seeking_talent in this Udacity Knowledge post:
      # https://knowledge.udacity.com/questions/75010
      if ('seeking_talent' in request.form):
        v.seeking_talent = (request.form['seeking_talent']=='y')
      else:
        v.seeking_talent = False
      v.seeking_description = request.form['seeking_description']
      
      db.session.commit()

    except:
      error = True
      #flash(sys.exc_info())
      db.session.rollback()
    
    finally:
      db.session.close()
      
    if not error:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully updated!')

    if error: 
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated')

    return redirect(url_for('show_venue', venue_id=venue_id))

  else:
    flash('You have Errors: ')
    for field, err in form.errors.items():
      flash(''.join(field).replace('_', ' ').title() + ' : \'' + ''.join(err) + '\'' )
    return render_template('forms/edit_venue.html', form=form, venue=v)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  error = False
  form = ArtistForm(request.form, meta={'csrf': False})

  if form.validate_on_submit():

    try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      image_link = request.form['image_link']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      website_link = request.form['website_link']

      if ('seeking_venue' in request.form):
        seeking_venue = (request.form['seeking_venue']=='y')
      else:
        seeking_venue = False

      seeking_description = request.form['seeking_description']
      
      artist = Artist(name=name, city=city, state=state,
      phone=phone, image_link=image_link, genres=genres, 
      facebook_link=facebook_link, website_link=website_link,
      seeking_venue=seeking_venue, seeking_description=seeking_description)

      db.session.add(artist)
      db.session.commit()

    except:
      error = True
      #flash(sys.exc_info())
      db.session.rollback()
    
    finally:
      db.session.close()
      
    if not error:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

    if error: 
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be created')

    return render_template('pages/home.html')

  else:
    flash('You have Errors: ')
    for field, err in form.errors.items():
      flash(''.join(field).replace('_', ' ').title() + ' : \'' + ''.join(err) + '\'' )
    return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  
  for show in Show.query.order_by(Show.start_time).all():
    show_data = {}
    show_data['venue_id'] = show.venue_id
    show_data['venue_name'] = Venue.query.get(show.venue_id).name
    show_data['artist_id'] = show.artist_id
    show_data['artist_name'] = Artist.query.get(show.artist_id).name
    show_data['artist_image_link'] = Artist.query.get(show.artist_id).image_link
    show_data['start_time'] = show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    #flash(show_data)
    data.append(show_data)
  
  #flash(data)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error = False
  form = ShowForm(request.form, meta={'csrf': False})

  if (form.validate_on_submit()):
    try:
      artist_id = request.form['artist_id']
      venue_id = request.form['venue_id']
      start_time = request.form['start_time']

      show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

      db.session.add(show)
      db.session.commit()

    except:
      error = True
      flash(sys.exc_info())
      db.session.rollback()

    finally:
      db.session.close()

    if error:
      flash('An error occurred. Show of Artist ' + request.form['artist_id'] + ' in Venue ' + request.form['venue_id'] + 'on ' + request.form['start_time'] + ' could not be listed!')
    
    if not error:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('Show of Artist ' + request.form['artist_id'] + ' in Venue ' + request.form['venue_id'] + ' on ' + request.form['start_time'] + ' was successfully listed!')
    
    return render_template('pages/home.html')
  
  else:
    flash('You have Errors: ')
    for field, err in form.errors.items():
      flash(''.join(field).replace('_', ' ').title() + ' : \'' + ''.join(err) + '\'' )
    return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
