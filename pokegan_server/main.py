import base64
import hashlib
import hmac
import json
import os
import tempfile

from flask import Flask, send_from_directory
from google.api_core.exceptions import NotFound
from google.cloud import storage
from werkzeug.exceptions import InternalServerError, HTTPException


GOOGLE_BUCKET = os.getenv('GOOGLE_BUCKET')


class FileNotFound(HTTPException):
    code = 404
    name = 'File Not Found'
    description = 'The requested image file was not found.'


# This is currently unused but is good to lockdown requests.
# There are probably better solutions through this from google
# as this causes the app to run.
class UnauthorizedRequest(HTTPException):
    code = 401
    name = 'Unauthorized Request'
    description = 'The request is not authorized to perform this action'


def authorizeRequest(request, secret):
    try:
        requestId = request.headers['X-Request-ID']
        requestSig = request.headers['X-Request-Signature']
    except KeyError:
        raise UnauthorizedRequest()
    else:
        computedSig = hmac.new(
            bytes(secret.encode('utf-8')),
            bytes(requestId.encode('utf-8')),
            digestmod=hashlib.sha256).digest()
        computedSig = base64.b64encode(computedSig).decode()
        if computedSig != requestSig:
            raise UnauthorizedRequest()


def create_app():

    app = Flask(__name__)

    # Return a detailed json response for exceptions
    @app.errorhandler(HTTPException)
    @app.errorhandler(InternalServerError)
    def handle_exception(error):
        response = error.get_response()
        responseDict = {
            'code': error.code,
            'name': error.name,
            'description': error.description
        }
        response.data = json.dumps(responseDict)
        response.content_type = 'application/json'
        return response

    # Return file data if found
    @app.route('/image/<filename>', methods=['GET'])
    def file_server(filename=None):

        storageClient = storage.Client()
        bucket = storageClient.get_bucket(GOOGLE_BUCKET)

        blob = bucket.blob(filename)
        # /temp dir is the only available filespace that is writable in app env
        # TODO: look at doing this all in memory to negate file io
        with tempfile.TemporaryDirectory() as tmpdirname:
            fullpath = os.path.join(tmpdirname, filename)
            try:
                blob.download_to_filename(fullpath)
            except NotFound:
                raise FileNotFound()
            return send_from_directory(tmpdirname, filename)

    return app


# WSGI friendly object for local and prod runtimes
app = create_app()
