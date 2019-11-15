
# [START gae_python37_render_template]
import datetime

from flask import Flask, render_template
from google.cloud import firestore
app = Flask(__name__)


@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_names = [{"first": "Josua", "ghost": "Bogle", "last": "Pedersen"},
                   {"first": "Xavier", "ghost": "Bhoot", "last": "Francis"},
                   {"first": "Tyler", "ghost": "Poltergeist", "last": "Durden"}
                   ]

    return render_template('index.html', names=dummy_names)


@app.route('/form')
def ghost_name_form():
    # Project ID is determined by the GCLOUD_PROJECT environment variable
    db = firestore.Client()

    return 'Hello, World'


@app.route('/results')
def ghost_name_results():
    return 'Hello, World'


def create_client(project_id):
    return datastore.Client(project_id)


def add_task(client, description):
    key = client.key('Task')

    task = datastore.Entity(
        key, exclude_from_indexes=['description'])

    task.update({
        'created': datetime.datetime.utcnow(),
        'description': description,
        'done': False
    })

    client.put(task)

    return task.key


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [START gae_python37_render_template]
