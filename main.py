"""
Entry point for ghost-namer app.
"""

# [START gae_python37_render_template]
import datetime
import random
import redis

from flask import Flask, render_template, request, redirect, url_for, session
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
from flask_session import Session
import lib.helper as lib

app = Flask(__name__)
app.config.from_object('config')
CLIENT = datastore.Client()
FIREBASE_API_KEY = app.config.get('FIREBASE_API_KEY')
FIREBASE_REQUEST_ADAPTER = requests.Request()

REDIS_HOST = app.config.get('REDIS_HOST')
REDIS_PORT = app.config.get('REDIS_PORT')
REDIS_PASSWORD = app.config.get('REDIS_PASSWORD')
app.config['SESSION_REDIS'] = redis.Redis(
    password=REDIS_PASSWORD, host=REDIS_HOST, port=REDIS_PORT)
Session(app)


@app.route('/')
def root(**kwargs):
    """ Returns the overview page. """

    user_entity = None
    error_message = kwargs.get('error_message')
    id_token = request.cookies.get("token")
    recent_ghosts_named = list(lib.fetch_latest_users(10))

    # If the user is logged in, personalise overview page.
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, FIREBASE_REQUEST_ADAPTER)
        except ValueError as exc:
            error_message = str(exc)

        if claims:
            user_entities = list(lib.fetch_user(claims['email']))

            if len(user_entities) > 0:
                user_entity = user_entities.pop(0)
                session['email'] = user_entity['email']
                session['first_name'] = user_entity['first_name']
                session['last_name'] = user_entity['last_name']
            else:
                error_message = 'User logged in but not found in datastore.'

    return render_template('index.html', user_data=user_entity,
                           error_message=error_message,
                           users=recent_ghosts_named)


@app.route('/auth')
def auth():
    """ Returns the authetication page. """

    return render_template('auth.html', api_key=FIREBASE_API_KEY)


@app.route('/form')
def user_name_form():
    """ Returns a form for the user to enter their first and last names. """

    email = None
    id_token = request.cookies.get("token")

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, FIREBASE_REQUEST_ADAPTER)
        except ValueError as exc:
            error_message = str(exc)

        if claims:
            email = claims['email']

    if not email:
        error_message = 'User not logged in.'
        return redirect(url_for('auth', error_message=error_message))

    # A new user has been authenticated. Store their email in session.
    session['email'] = email

    return render_template('form.html')


@app.route('/results', methods=['POST', 'GET'])
def ghost_name_results():
    """ Returns the ghost name selection page with three ghost names. """

    if not session.get('email'):
        error_message = 'User not logged in.'
        return redirect(url_for('auth', error_message=error_message))

    error_message = None

    # User wants to change their ghost name.
    if request.method == "GET":
        first_name = session.get('first_name')
        last_name = session.get('last_name')
    # A new user wants to pick their ghost name.
    else:
        first_name = request.form.get("user-first-name")
        last_name = request.form.get("user-last-name")
        session['first_name'] = first_name
        session['last_name'] = last_name

    # Get three available ghost entities at random.
    query = CLIENT.query(kind='ghosts')
    query.add_filter('available', '=', True)
    ghost_entities = list(query.fetch())

    if len(ghost_entities) < 3:
        # Uh oh. We've run out of ghosts... 😞
        # No worries, rinse and repeat.
        lib.flush_data()
        lib.seed_data()
        ghost_entities = list(query.fetch())

    ghosts = random.sample(ghost_entities, 3)

    return render_template('results.html', ghosts=ghosts, first_name=first_name,
                           last_name=last_name, error_message=error_message)


@app.route('/store', methods=['POST'])
def store_ghost_name():
    """ Stores the user and ghost details to datastore. """

    if not session.get('email'):
        error_message = 'User not logged in.'
        return redirect(url_for('auth', error_message=error_message))

    error_message = None
    email = session.get('email')
    first_name = session.get('first_name')
    last_name = session.get('last_name')
    ghost_name = request.form.get("selected-ghost-name")
    ghost_id = request.form.get("selected-ghost-id")
    user_entity = list(lib.fetch_user(email))

    # User exists; update their details.
    if len(user_entity) > 0:
        # Update old Ghost
        user_entity = user_entity.pop(0)
        previous_ghost_entity = CLIENT.get(
            CLIENT.key('ghosts', int(user_entity['ghost_id'])))
        previous_ghost_entity['available'] = True
        previous_ghost_entity['updated'] = datetime.datetime.utcnow()

        with CLIENT.transaction():
            # Update User
            user_entity['updated'] = datetime.datetime.utcnow()
            user_entity['ghost_name'] = ghost_name
            user_entity['ghost_id'] = ghost_id
            user_entity['first_name'] = first_name
            user_entity['last_name'] = last_name
            CLIENT.put(user_entity)
            print('Updated User: {}'.format(user_entity))

            # Update chosen Ghost
            ghost_entity = CLIENT.get(CLIENT.key('ghosts', int(ghost_id)))
            ghost_entity['available'] = False
            ghost_entity['updated'] = datetime.datetime.utcnow()
            CLIENT.put_multi(
                [previous_ghost_entity, user_entity, ghost_entity])

    # A new user has arrived!
    else:
        with CLIENT.transaction():
            # Create User
            user_entity = datastore.Entity(CLIENT.key('users'))
            user_entity.update({
                'updated': datetime.datetime.utcnow(),
                'first_name': first_name,
                'last_name': last_name,
                'ghost_name': ghost_name,
                'ghost_id': ghost_id,
                'email': email
            })
            print('New User: {}'.format(user_entity))

            # Update chosen Ghost
            ghost_entity = CLIENT.get(CLIENT.key('ghosts', int(ghost_id)))
            ghost_entity['available'] = False
            ghost_entity['updated'] = datetime.datetime.utcnow()
            CLIENT.put_multi([user_entity, ghost_entity])

    return redirect(url_for('root', error_message=error_message))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
# [START gae_python37_render_template]
