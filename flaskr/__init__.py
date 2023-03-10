import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)



    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_categories():
        # getting the categories of the questions
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {
                    category.id: category.type for category in categories
                }
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=["GET"])
    def get_questions():
        # getting the list of all the questions 
        all_selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, all_selection)

        categories = Category.query.order_by(Category.id).all()
        each_category = {category.id: category.type for category in categories}

        if len(current_questions) == 0:
            abort(404)

        else:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(all_selection),
                'categories': each_category,
                'current_category': None
            })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        # deleting a question
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            all_selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, all_selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question.id,
                    "question": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def post_question():
        # posting a question based on data gotten from the user 
        body = request.get_json()

        if "question" in body and "answer" in body and "difficulty" in body and "category" in body:
            new_question = body.get("question")
            new_answer = body.get("answer")
            new_category = body.get("category")
            new_difficulty = body.get("difficulty")
        
        else:
            abort(422)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    def search_question():
        # getting questions that correlate to the given search term
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        try:
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            each_question = paginate_questions(request, questions)

            return jsonify({
              'success': True,
              'questions': each_question,
              'total_questions': len(each_question),
              'current_category': None,
            })
        except Exception:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_by_category(category_id):
        # getting questions with the given category_id

        try:
            questions = Question.query.filter(Question.category == category_id).all()
            each_questions = paginate_questions(request, questions)


            return jsonify({
                'success': True,
                'questions': each_questions,
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def retrieve_quizzes():
        '''
        Endpoint to get questions to play the quiz.
        '''
        try:
        # getting the question
            body = request.get_json()
        
            quiz_category = body.get('quiz_category', None)
            # getting the previous questions
            previous = body.get('previous_questions', None)
            category_id = quiz_category.get('id')
            
            # validating that the question has not been picked
            if category_id == 0:
                 available_questions = Question.query.all()
            else:
                available_questions = Question.query.filter_by(category=category_id).filter(Question.id.notin_((previous))).all()

            new_question = available_questions[random.randrange(0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except Exception:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    # handling error in the case of a request that couldn't be found
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "request not found"}),
            404,
        )

    @app.errorhandler(422)
    # handling error in the case of a request that the system understands but can't process
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    # handling errors in the case of a bad request
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    # handling error in the case of an unauthorised method
    def invalid_method(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )
    return app

