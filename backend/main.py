from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from routes.user_route import user_bp
from routes.question_route import question_bp
from routes.course_route import course_bp
from routes.subunit_route import subunit_bp
from routes.bookmark_route import bookmark_bp
# from routes.mission_route import mission_bp
# starting up flask app, registers routes and enables CORS
app = Flask(__name__)
CORS(app)

# loads the routes dynamically from the route files
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(question_bp, url_prefix="/api")
app.register_blueprint(course_bp, url_prefix="/api")
app.register_blueprint(subunit_bp, url_prefix="/api")
app.register_blueprint(bookmark_bp, url_prefix="/api")
# app.register_blueprint(mission_bp, url_prefix="/api")


@app.route('/static/profile_pictures/<path:filename>')
def serve_profile_picture(filename):
    return send_from_directory(os.path.join(app.root_path, 'static/profile_pictures'), filename)

# they are all structured to have prefix /api for restful api consistency,
# and to avoid conflicts with frontend routes
if __name__ == "__main__":
    app.run(port=8080, debug=True)