import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.HOST = 'localhost:5432'
        self.USER = 'postgres'
        self.PASSWORD = '1530'
        self.database_name = 'trivia'
        self.database_path = "postgres://{}:{}@{}/{}".format(
        self.USER, self.PASSWORD, self.HOST, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        # testing to get the paginated questions
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_questions_page_404(self):
        # testing in the case of an error while getting paginated questions
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'request not found')

    def test_delete_question(self):
        # testing deleting a question
        res = self.client().delete('/questions/20')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'],20)

    def test_delete_question_id_404(self):
        # testing trying to delete an unexisting question
        res = self.client().delete('/questions/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        

    def test_create_question(self):
        # testing creating a new question
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'difficulty': 2,
            'category': 4
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_question_not_allowed(self):
        # testing posting a question through an unallowed method 
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 4
        }
        res = self.client().post('/questions/45', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_search_questions(self):
        # testing searching a question with a search term
        search = {'searchTerm': 'Who is', }
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        

    def test_search_no_result(self):
        # testing searching a question with a search term but no result
        search = {
            'searchTerm': 'atu bi en yan gba dodi',
        }
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], None)

    def test_get_questions_by_category(self):
        # testing getting questions based on categories
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 4)

    def test_get_categories(self):
        # testing getting categories
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_quiz(self):
        # testing playing the quiz
        play_quiz = {
            'previous_questions': [4],
            'quiz_category': {'type': 'History', 'id': '4'}
        }
        res = self.client().post('/quizzes', json=play_quiz)
        data = json.loads(res.data)
        question = data['question']

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 4)
        self.assertIn('question', question)
        self.assertIn('answer', question)
        self.assertIn('difficulty', question)
        self.assertIn('id', question)

    def test_quiz_not_found(self):
        # testing for when a requested question isn't found
        quiz = {'previous_questions': []}
        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        

    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()