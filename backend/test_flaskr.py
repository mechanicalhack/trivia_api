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

    def test_get_questions(self):
        """ Get Questions """
        res = self.client().get('/questions')

        data = json.loads(res.data)
  
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

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
        """ Delete Question 422 Error"""
        res = self.client().delete('/questions/1')
        
        self.assertEqual(res.status_code, 422)

    def test_add_new_question(self):
        res = self.client().post('/questions', json={'question': 'new question', 'answer': 'new answer', 'category': 1, 'difficulty': 2})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], "new question")

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'new'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], [{'answer': 'new answer', 'category': 1, 'difficulty': 2, 'id': 24, 'question': 'new question'}])
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], {})

    def test_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], {'1': 'Science'} )
    
    def test_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'type': 'Science', 'id': 1}})
        data = json.loads(res.data)
     
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 1)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()