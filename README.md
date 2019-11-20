# [ghost-namer](http://strange-sun-258602.appspot.com/)

An app that provides the user a ghost name.

Routing and logic in `main.py`. Datastore helper functions in `lib\helper.py`.

## Stack
- Google App Engine
- Cloud Datastore
- Firebase Auth
- Flask
- Flask_Session + Redis

## Entity schema
```
User {
  'email': string
  'first_name': string
  'ghost_name': string
  'last_name': string
  'ghost_id': string
  'updated': timestamp
}
```
```
Ghost {
  'id': int
  'name': string
  'description': string
  'available': boolean
  'updated': timestamp
}
```

## Design
Ghost entities are seeded to the datastore on initial deployment, with the `available` attribute set to `True` for all of them. Max user count is 40. The datastore is reset every 41st user.

### New / returning user
When a new user or a user who has previously created an account arrives, they log-in using Google auth and are asked to provide their first and last names. Email and names are stored in the session (server-side in Redis) by this point. 3 available entities are retrieved at random from the datastore and presented to the user. Once they make their choice, the selected ghost is retrieved from the form and the User and Ghost entities are updated. If the user already exists in the datastore, the existing Entity and the previously chosen ghost are updated in addition to the newly chosen ghost. The user is redirected to the home page, where the logged-in user flow is initiated.

### Logged-in user
When a user arrives, and a Google auth token exists on the client-side, their details are retrieved from the datastore to provide a personalised landing page. In this flow the user has access to the home page and the ghost name selection page. Once the user selects a ghost name and submits the form, the previously chosen ghost entity, the user entity, and the newly selected ghost entity are all updated. The user is redirected to the home page, where the logged-in user flow is initiated.

## Credits
- `ghost.svg` courtesy the [OpenMoji](https://github.com/hfg-gmuend/openmoji) project.
- `dropdown-selector.{js, css}` courtesy of [Alessandro Falchi](https://codepen.io/afalchi82).

## License
MIT