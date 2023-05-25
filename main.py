import os
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db

app = None
api = None
def create_app():
    app = Flask(__name__, template_folder="templates")
    IMAGES_FOLDER = os.path.join('static', 'images')
    app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api

app, api = create_app()
app.secret_key = os.urandom(24)

# Import all the controllers so they are loaded
from application.controllers import *

# Add all restful controllers
from application.api import *
api.add_resource(UserAPI, "/api/user","/api/user/<string:username>")
api.add_resource(BlogAPI,  "/api/blog/<post_id>", "/api/blog/<username>/addpost")
api.add_resource(UserBlogAPI, "/api/userblogs/<username>")

if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0',port=5555, debug=True)
