import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    current_questions = []
    i = 0
    for question in selection:
      if i >= start and i < end:
        current_questions.append(question)
      i+=1

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"*": {"origins": "*"}})

  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  # End Points
  @app.route('/categories')
  def retrieve_categories():
    data = Category.query.all()
    categories = {}
    for c in data:
      categories[c.id] = c.type

    return jsonify({
      'success': True,
      'categories': categories
    })

  @app.route('/questions')
  def retrieve_questions():
    data = Question.query.all()
    questions = []
    for q in data:
      questions.append({
        'id': q.id,
        'question': q.question,
        'answer': q.answer,
        'difficulty': q.difficulty,
        'category': q.category
      })

    current_questions = paginate_questions(request, questions)

    all_categories = Category.query.all()
    categories = {}
    for category in all_categories:
      categories[category.id] = category.type

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': categories,
      'current_category': {}
    })

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def remove_question(id):
    try:
      question_to_delete = Question.query.get(id)
      question_to_delete.delete()
      
      return jsonify({
        'success': True,
        'deleted': question_to_delete.id
      })
    except:
      abort(422)

  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    new_question = body.get('question')
    new_answer = body.get('answer')
    new_category = body.get('category')
    new_difficulty = body.get('difficulty')

    if new_question == None or new_answer == None or new_difficulty == None or new_category == None:
      abort(422)
    try:
      question = Question(new_question, new_answer, new_category, new_difficulty)
      question.insert()

      return jsonify({
        'success': True,
        'question': new_question
      })
    except:
      abort(422)

  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()

    search_term = body.get('searchTerm')
    
    if not isinstance(search_term, str):
      abort(422)
    
    results = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
    number_of_results = Question.query.filter(Question.question.ilike('%' + search_term + '%')).count()
    
    questions = []
    for q in results:
      questions.append({
        'id': q.id,
        'question': q.question,
        'answer': q.answer,
        'difficulty': q.difficulty,
        'category': q.category
      })

    current_questions = paginate_questions(request, questions)
    
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': number_of_results,
      'current_category': {}
    })

  @app.route('/categories/<int:id>/questions')
  def retrieve_questions_by_category(id):
    
    filtered_questions = Question.query.filter_by(category=str(id)).all()
    filtered_questions_count = len(Question.query.filter_by(category=str(id)).all())

    questions = []
    for q in filtered_questions:
      questions.append({
        'id': q.id,
        'question': q.question,
        'answer': q.answer,
        'difficulty': q.difficulty,
        'category': q.category
      })

    current_questions = paginate_questions(request, questions)

    current_category_result = Category.query.get(id)
    current_category = {}
    current_category[current_category_result.id] = current_category_result.type

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': filtered_questions_count,
      'current_category': current_category
    })

  @app.route('/quizzes', methods=['POST'])
  def retrieve_questions_for_quizzes():
    body = request.get_json()

    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')

    if(quiz_category['id'] == 0):
      filtered_questions_by_category = Question.query.all()
    else:
      filtered_questions_by_category = Question.query.filter_by(category=str(quiz_category['id'])).all()
    filtered_questions_by_previous_questions = [question for question in filtered_questions_by_category if question.id not in previous_questions]

    if len(filtered_questions_by_previous_questions) > 0:
      random_new_question = random.choice(filtered_questions_by_previous_questions)
      new_quiz_question = {
        'id': random_new_question.id,
        'question': random_new_question.question,
        'answer': random_new_question.answer,
        'category': random_new_question.category,
        'difficulty': random_new_question.difficulty
      }
    else:
      new_quiz_question = None
    
    return jsonify({
      'success': True,
      'question': new_quiz_question
    })
  
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False, 
          "error": 422,
          "message": "Unprocessable"
      }), 422

  @app.errorhandler(404)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "Not Found"
      }), 404

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 400,
          "message": "Bad Request"
      }), 400

  @app.errorhandler(405)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 405,
          "message": "Method Not Allowed"
      }), 405

  @app.errorhandler(500)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 500,
          "message": "Internal Server Error"
      }), 500

  return app

    