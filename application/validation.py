from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('User not found.', status_code)
    
class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

class InvalidCredentials(HTTPException):
    def __init__(self, status_code):
        self.response = make_response("Invalid login details.", status_code)

class BlogNotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('Blog not found.', status_code)
    
class NoBlogsForUser(HTTPException):
    def __init__(self, status_code):
        self.response = make_response("No blogs exist for user.", status_code)