"""
Helper function library.
"""

import csv
import datetime
from google.cloud import datastore

CLIENT = datastore.Client()


def fetch_user(email):
    """
    Fetches the user with the given email.

    Args:
        email: email address of the user.
    """

    query = CLIENT.query(kind='users')
    query.add_filter('email', '=', email)
    user_entity = query.fetch()
    return user_entity


def delete_user(user):
    """
    Deletes the given user Entity from the datastore.

    Args:
        user: User Entity to be deleted.
    """

    # Update ghost entity
    ghost_entity = CLIENT.get(
        CLIENT.key('ghosts', int(user['ghost_id'])))
    ghost_entity['available'] = True

    key = CLIENT.key('users', user.id)
    CLIENT.delete(key)

    with CLIENT.transaction():
        CLIENT.put(ghost_entity)


def fetch_latest_users(limit):
    """
    Fetches the n latest users from the datastore.

    Args:
        limit: number of users to fetch.
    """

    query = CLIENT.query(kind='users')
    query.order = ['-updated']
    user_entities = query.fetch(limit=limit)
    return user_entities


def flush_data():
    """
    Removes all Entities of all Kinds from datastore.
    """

    user_query = CLIENT.query(kind='users')
    ghost_query = CLIENT.query(kind='ghosts')
    user_entities = list(user_query.fetch())
    ghost_entities = list(ghost_query.fetch())

    if len(user_entities) > 0:
        user_keys = []
        for user in user_entities:
            user_keys.append(CLIENT.key('users', user.id))

        CLIENT.delete_multi(user_entities)

    if len(ghost_entities) > 0:
        ghost_keys = []
        for ghost in ghost_entities:
            ghost_keys.append(CLIENT.key('ghosts', ghost.id))

        CLIENT.delete_multi(ghost_entities)


def seed_data(data_file='../data/ghost-names.csv'):
    """
    Seeds the datastore with ghost name values from the CSV file.

    Args:
        data_file: Optional. Path to CSV file containing
            ghost names and their descriptions.

    Raises:
        Exception: An error occurred while reading the CSV file.
        Exception: An error occurred while persisting entity to datastore.
    """

    ghosts = []

    try:
        print('Reading {}...'.format(data_file))
        with open(data_file) as csv_file:
            names_reader = csv.reader(csv_file, delimiter=',')

            for row in names_reader:
                ghosts.append((row[0], row[1]))
    except:
        raise Exception('Error reading {}'.format(data_file))

    print('Ghosts read: {}'.format(len(ghosts)))

    try:
        print('Writing to datastore...')
        ghost_entities = []

        for idx, val in enumerate(ghosts):
            ghost_name, description = val
            ghost_entity = datastore.Entity(CLIENT.key(
                'ghosts', idx + 1), exclude_from_indexes=['description'])
            ghost_entity.update({
                'updated': datetime.datetime.utcnow(),
                'name': ghost_name,
                'description': description,
                'available': True
            })
            ghost_entities.append(ghost_entity)

        CLIENT.put_multi(ghost_entities)
        print('Done, {} ghosts inserted into datastore.'
              .format(len(ghost_entities)))
    except:
        raise Exception('Error writing ghosts to datastore.')
