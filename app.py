from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
import os

# Initialize the Flask application
app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lessons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# Define the Lesson Model
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)

# API Resource for handling single lesson operations (GET, PUT, DELETE)
class LessonResource(Resource):
    # GET request: Retrieve a lesson by its ID
    def get(self, lesson_id):
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {'message': 'Lesson not found'}, 404
        return {'id': lesson.id, 'title': lesson.title, 'description': lesson.description}

    # PUT request: Update a lesson by its ID
    def put(self, lesson_id):
        data = request.get_json()
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {'message': 'Lesson not found'}, 404
        lesson.title = data.get('title', lesson.title)
        lesson.description = data.get('description', lesson.description)
        db.session.commit()
        return {'message': 'Lesson updated'}

    # DELETE request: Remove a lesson by its ID
    def delete(self, lesson_id):
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {'message': 'Lesson not found'}, 404
        db.session.delete(lesson)
        db.session.commit()
        return {'message': 'Lesson deleted'}

# API Resource for handling multiple lessons (GET, POST)
class LessonListResource(Resource):
    # GET request: Retrieve all lessons
    def get(self):
        lessons = Lesson.query.all()
        return [{'id': l.id, 'title': l.title, 'description': l.description} for l in lessons]

    # POST request: Add a new lesson
    def post(self):
        data = request.get_json()
        existing_lesson = Lesson.query.filter_by(title=data['title']).first()

        # Prevent duplicate lesson
        if existing_lesson:
            return {'message': 'Lesson with this title already exists!'}, 400  # Prevent duplicates

        new_lesson = Lesson(title=data['title'], description=data['description'])
        db.session.add(new_lesson)
        try:
            db.session.commit()
            return {'message': 'Lesson added'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error adding lesson: {str(e)}'}, 500

# Register API Endpoints
api.add_resource(LessonListResource, '/api/lessons')
api.add_resource(LessonResource, '/api/lessons/<int:lesson_id>')

# Serve the Frontend
@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Initialize the database
    app.run(debug=True)
