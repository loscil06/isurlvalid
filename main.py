"""Make a server that accepts a url and returns true or false."""
import requests
from flask import Flask, jsonify, request
from marshmallow import Schema, fields, ValidationError


# Define schemas
class ParamsSchema(Schema):
    """Validate params of this application."""

    url = fields.Url(required=True)


# Define custom exceptions
class UrlNotValidException(Exception):
    """Define an invalid usage exception."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Self-explanatory."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Return a dict of self."""
        return {"message": self.message, "payload": self.payload}


# Define the app
app = Flask(__name__)

# Define error handling
@app.errorhandler(UrlNotValidException)
def handle_invalid_usage(error):
    """Define error handling."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Define error handling."""
    response = jsonify(error.messages)
    response.status_code = 400
    return response

# Define routes
@app.route("/")
def mainroute():
    """Define the main route of this app."""
    args = ParamsSchema().load(data=request.args)
    response = requests.get(args["url"])
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise UrlNotValidException(
            message="url not valid",
            status_code=response.status_code,
            payload=response.text
        )
    return jsonify({"success": True}), response.status_code
