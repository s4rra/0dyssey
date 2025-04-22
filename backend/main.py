from flask import Flask
from flask_cors import CORS
from routes.user_route import user_bp
from routes.question_route import question_bp
from routes.course_route import course_bp
from routes.subunit_route import subunit_bp
from routes.answer_route import answer_bp
from routes.performance_route import performance_bp
#starting up flask app, registers routes and enables CORS
from routes.mission_route import mission_bp 
from routes.bookmark_route import bookmark_bp
from routes.shop_route import shop_bp

# from routes.performance_route import performance_bp
#starting up flask app, registers routes and enables CORS
app = Flask(__name__)
CORS(app)

# loads the routes dynamically from the route files
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(question_bp, url_prefix="/api")
app.register_blueprint(course_bp, url_prefix="/api")
app.register_blueprint(subunit_bp, url_prefix="/api")
app.register_blueprint(answer_bp, url_prefix="/api")
app.register_blueprint(performance_bp, url_prefix="/api") 
app.register_blueprint(mission_bp, url_prefix="/api")   
app.register_blueprint(bookmark_bp, url_prefix="/api")
app.register_blueprint(shop_bp, url_prefix="/api")


if __name__ == "__main__":
    app.run(port=8080, debug=True)
