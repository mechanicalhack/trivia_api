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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
    
    def test_get_categories(self):
        """ Get Categories """
        res = self.client().get('/categories')

        data = json.loads(res.data)
  
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])

    def test_get_categories_404(self):
        """ Get Categories 404 Error """
        res = self.client().get('/categories/1')

        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_questions(self):
        """ Get Questions """
        res = self.client().get('/questions')

        data = json.loads(res.data)
  
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_405(self):
        """ Get Questions 405 Error """
        res = self.client().get('/questions/1')

        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'Method Not Allowed')

    def test_delete_question(self):
        """ Delete Question """
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        res1 = self.client().delete('/questions/' + str(data['questions'][0]['id']))
        data1 = json.loads(res1.data)
        
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(data1['success'],True)
        self.assertEqual(data1['deleted'],data['questions'][0]['id'])

    def test_delete_question_422(self):
        """ Delete Question 422 Error """
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_add_new_question(self):
        """ Add New Question """
        res = self.client().post('/questions', json={'question': 'new question', 'answer': 'new answer', 'category': 1, 'difficulty': 2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], "new question")

    def test_add_new_question_422(self):
        """ Add New Question 422 Error """
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_search_question(self):
        """ Search Questions """
        res = self.client().post('/questions/search', json={'searchTerm': 'new'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], [{'answer': 'new answer', 'category': 1, 'difficulty': 2, 'id': 24, 'question': 'new question'}])
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], {})

    def test_search_question_422(self):
        """ Search Questions 422 Error """
        res = self.client().post('/questions/search', json={'searchTerm': 1})
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_questions_by_category(self):
        """ Questions By Category """
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], {'1': 'Science'} )

    def test_questions_by_category_500(self):
        """ Questions By Category 500 Error """
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['message'], 'Internal Server Error')
    
    def test_quiz(self):
        """ Quiz """
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'type': 'Science', 'id': 1}})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 1)

    def test_quiz_500(self):
        """ Quiz 500 Error """
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['message'], 'Internal Server Error')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()