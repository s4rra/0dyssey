from flask import Flask
from flask_cors import CORS
from routes.user_route import user_bp
from routes.question_route import question_bp
from routes.course_route import course_bp

#starting up flask app, registers routes and enables CORS
app = Flask(__name__)
CORS(app)

# loads the routes dynamically from the route files
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(question_bp, url_prefix="/api")
app.register_blueprint(course_bp, url_prefix="/api")
#they are all structured to have prefix /api for restful api  consistency, and to aviod conflicts with frontend routes

if __name__ == "__main__":
    app.run(port=8080, debug=True)
