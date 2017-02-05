import os
import unittest
from unittest import TestCase
from flask import abort, jsonify, make_response

from app import create_app, db
from app.models import User, Request, Proposal, MealDate


def make_app():
    config_name = 'testing'
    app = create_app(config_name)
    app.config.update(
        SQLALCHEMY_DATABASE_URI='mysql://root:1@localhost/meatneat1'
    )
    return app

class TestBase(TestCase):


    def setUp(self):
        """
        Will be called before every test
        """
        self.app = make_app()
        db.create_all()

        # create test user
        user = User(username="xavier", password="1")

        # save users to database
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        """
        Will be called after every test
        """

        db.session.remove()
        db.drop_all()


class TestErrorPages(TestBase):

    def test_403_forbidden(self):
        # create route to abort the request with the 403 Error
        @self.app.route('/403')
        def forbidden_error():
            abort(403)

        response = self.client.get('/403')
        self.assertEqual(response.status_code, 403)
        self.assertTrue("403 Error" in response.data)

    def test_404_not_found(self):
        response = self.client.get('/nothinghere')
        self.assertEqual(response.status_code, 404)
        error = {'errors': 'Page Not Found'}
        self.assertDictEqual(error, response)

    def test_500_internal_server_error(self):
        # create route to abort the request with the 500 Error
        @self.app.route('/500')
        def internal_server_error():
            abort(500)

        response = self.client.get('/500')
        self.assertEqual(response.status_code, 500)
        self.assertTrue("500 Error" in response.data)


if __name__ == '__main__':
    unittest.main()