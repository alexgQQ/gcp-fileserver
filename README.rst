# Pokegan Server

This code is meant to serve the file output from the pokegan inference as a 
CDN sort of function from a google bucket. This is meant to be simple and 
lightweight to run on [minimal gcloud app engine](https://cloud.google.com/appengine/docs/standard/runtimes).

## Config

A few environmental varaiables need to be defined properly.
```
FLASK_ENV=development  # or production
FLASK_APP=pokegan_server.main:app  # app import for runtime (local only)
GOOGLE_BUCKET=bucket-name  # bucket name for files
GOOGLE_APPLICATION_CREDENTIALS=/path/to/app.json  # default creds (local only)
```

## Run

```
poetry install
poetry run flask run
```

## Deploy

TODO: Do i even need an endpoints config deploy?

```
poetry export --without-hashes > pokegan_server/requirements.txt
gcloud -q app deploy app.yaml
```
