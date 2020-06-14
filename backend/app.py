import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json
import sys
from sqlalchemy.sql import func

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app)
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    def paginate_questions(request, question_list):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        formatted_question_list = [question.format()
                                   for question in question_list]
        return formatted_question_list[start:end]

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    class Object:
        def toJSON(self):
            return json.dumps(
                self,
                default=lambda o: o.__dict__,
                sort_keys=True,
                indent=4)

    @app.route('/categories')
    def get_categories():
        success = True
        body = {}
        try:
            category_list = Category.query.all()
            formatted_category_list = [
                category.format() for category in category_list]
            print(formatted_category_list)
        except BaseException:
            success = False
            print(sys.exc_info())
        if not success:
            abort(422)
        else:
            success = True
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in category_list}
            # 'categories': formatted_category_list
        })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def get_questions():
        success = True
        body = {}
        page = request.args.get('page', 1, type=int)

        try:
            question_list = Question.query.all()
            paginated_question_list = paginate_questions(
                request, question_list)
            category_list = Category.query.all()
            formatted_category_list = [
                category.format() for category in category_list]
        except BaseException:
            success = False
            print(sys.exc_info())
        if not success:
            abort(422)
        else:
            if not len(paginated_question_list):
                abort(404)
            else:
                success = True
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in category_list},
            'questions': paginated_question_list,
            'total_questions': len(question_list),
            # 'categories': formatted_category_list,
            'current_category': 'None',
            'currentPage': page
        })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>/', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(422)

            question.delete()
            question_list = Question.query.all()
            paginated_question_list = paginate_questions(
                request, question_list)
            return jsonify({
                'success': True,
                'questions': paginated_question_list,
                'total_questions': len(question_list),
                'question_deleted': question_id,
            })

        except BaseException:
            abort(422)

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def post_question():
        success = False
        try:
            question = request.json.get('question', None)
            answer = request.json.get('answer', None)
            difficulty = request.json.get('difficulty', None)
            category = request.json.get('category', None)
            if not (question and answer and category and difficulty):
                return abort(
                    400,
                    'Required question details are missing. Please retry',
                    'body')
            question_instance = Question(
                question, answer, category, difficulty)
            question_instance.insert()
            success = True
            question_list = Question.query.all()
            paginated_question_list = paginate_questions(
                request, question_list)
            return jsonify({
                'success': True,
                'questions': paginated_question_list,
                'total_questions': len(question_list),
                'question_added': question_instance.format()
            })
        except BaseException:
            return abort(422, 'An Error occurred, please retry', 'body')

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            page = request.args.get('page', 1, type=int)
            search_term = request.json.get('searchTerm', '')
            print(search_term)
            search = "%{}%".format(search_term)
            print(search)
            search_response = Question.query.filter(
                Question.question.ilike(search)).all()
            print(search_response)
            paginated_question_list = paginate_questions(
                request, search_response)
            print(paginated_question_list)
            if not len(paginated_question_list):
                abort(404)
            return jsonify({
                "success": True,
                "questions": paginated_question_list,
                "total_questions": len(search_response),
                "currentPage": page
            })
        except BaseException:
            print(sys.exc_info())
            return abort(404)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:ctgy_id>/questions')
    def get_category_wise_questions(ctgy_id):
        try:
            print(ctgy_id)
            question_list = Question.query.filter(
                Question.category == ctgy_id).all()
            print(question_list)
            if question_list is None:
                abort(404)

            paginated_question_list = paginate_questions(
                request, question_list)
            return jsonify({
                'success': True,
                'questions': paginated_question_list,
                'total_questions': len(question_list),
                'current_category': ctgy_id
            })
        except BaseException:
            abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def post_next_question():
        print('hi')

        try:
            prev_question_list = request.json.get('previous_questions')
            print(prev_question_list)
            category_id = int(request.json.get('quiz_category').get('id'))
            print(category_id)
            if len(prev_question_list) > 0 and category_id != 0:
                question = Question.query.filter(
                    Question.category == category_id).filter(
                    Question.id.notin_(prev_question_list)).order_by(
                    func.random()).first()
            elif len(prev_question_list) <= 0 and category_id != 0:
                question = Question.query.filter(
                    Question.category == category_id).order_by(
                    func.random()).first()
            elif len(prev_question_list) > 0 and category_id == 0:
                question = Question.query.filter(
                    Question.id.notin_(prev_question_list)).order_by(
                    func.random()).first()
            else:
                question = Question.query.order_by(func.random()).first()

            print(question)
            if question is None:
                return jsonify({
                'success': False,
                'question': None,
                'current_category': category_id
                })
            else :
                return jsonify({
                    'success': True,
                    'question': question.format(),
                    'current_category': category_id
                })
        except BaseException:
            print(sys.exc_info())
            abort(422)
    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def not_processed(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Request cannot be processed'
        }), 422

    return app
