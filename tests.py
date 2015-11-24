import os
import unittest
from server import app
from model import User, Recipe, Category, Ingredient, Yummlyrecipe, Yummlyuser, connect_to_db, db

APP_SECRET_KEY=os.environ.get("APP_KEY")


class RecipeTests(unittest.TestCase):
    """ Test for Recipebook app for functions that don't require sessions."""

    def setUp(self):
        #set up fake test browser
        self.client = app.test_client()

        # connect to database
        connect_to_db(app, "sqlite:///")
        db.create_all()

        # load_test_data():
             # put in users to test login


        # This line makes a 500 error in a route raise an error in a test
        app.config['TESTING'] = True

        app.debug = False

        # Recipe.create_recipe("testtitle", 3, 1, "test preparation", 6, "test.jpg")

        # Ingredient.create_ingredient("sugar", 2, "cup", 1)


##############################################################################
# Test any functions that only render a template.

    def test_load_homepage(self):
        """ Test to see if the index page comes up."""

        result = self.client.get('/')
        # print dir(result) to see what methods are available for result
        
        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn("<p> Take your recipe anywhere you go </p>", result.data)


    def test_load_signup(self):
        """ Test to see if the signup page comes up."""

        result = self.client.get('/signup')

        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('<form action="/signup-confirm" method="POST">', result.data)


    def test_load_signin(self):
        """ Test to see if the signin page comes up."""

        result = self.client.get('/signin')

        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('<form action="/signin-confirm" method="POST">', result.data)


    def test_load_recipe_form(self):
        """ Test to see if the splash page comes up."""

        # Signup user
        self.signup()

        #signin user
        self.login()

        # and then proceed with the code below.
        result = self.client.get('/recipeform')

        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('Add New Recipe', result.data)


    def test_load_logout(self):
        """ Test to see if logout occurs properly."""

        #send a post to signin a user, and then check to see if you can sign them out
        self.signup()

        self.login()

        result = self.client.get('/logout', follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('You are successfully Logged Out.', result.data)

    
    def test_load_recipe_form(self):
        """ Test to see if the recipe form comes up."""

        self.signup()

        self.login()

        result = self.client.get('/recipeform')
        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('<h3> Categorize this recipe </h3>', result.data)

    def test_load_recipe_list(self):
        """ Test to see if the recipe list template comes up"""

        self.signup()

        self.login()

        result = self.client.get('/recipe-list')
        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('<p>Search Results:</p>', result.data)

    # ##########################################################################################
    # # Test any functions that will query data.

    def test_process_signup_new_user(self):
        """Test to see if the signup form will process new user properly"""

        result = self.signup()
        self.assertIn('<a href="/signin">Sign In', result.data)
        self.assertIn('Your account has been created successfully', result.data)

    def test_process_signin_new_user(self):
        """Test to see if the signin form will process new user properly"""

        self.signup()
        result = self.login()

        self.assertEqual(result.status_code, 200)
        self.assertIn('<h3> Categorize this recipe </h3>', result.data)

    def test_process_signup_existing_user(self):
        """Test to see if the user already exist after processing signup"""

        self.signup()
        result = self.signup()

        self.assertEqual(result.status_code, 200)
        self.assertIn('already have an account, please sign in.', result.data)

    def test_invalid_user_signin(self):
        """Test to see if user can signin without signing up."""

        result = self.login()

        self.assertIn('sername and password combination are Incorrect', result.data)

    # def test_process_recipe_form(self):
    #     """ Test to see new recipe gets submitted properly"""

    #     self.signup()
    #     self.login()



    #     self.confirm_recipe()
    #     # print result

    #     # self.assertIn('<p> User Recipes: Total Number', result.data)
    #     # self.assertEqual(result.status_code, 200)


    # ##########################################################################################
    # # Helper function
    def signup(self):
        """ sign in a user as above """

        return self.client.post('/signup-confirm',
                                  data={'username': "sane",
                                        'password': "smith",
                                        'email': "sane@sane.com"},
                                  follow_redirects=True)


    def login(self):
        """ log in a user as above"""

        return self.client.post('/signin-confirm',
                                data={'username': "sane",
                                      'password': "smith"},
                                follow_redirects=True)

    # def confirm_recipe(self):
    #     """ post new recipe"""
    #     print dir(self.client)

    #     result = self.client.post('/recipeform-confirm',
    #                             data={'title': 'testtitle',
    #                                   'category_name': '2',
    #                                   'preparation': 'test preparation',
    #                                   'yields': '5',
    #                                   'image': 'http://www.ndtv.com/cooks/images/rogan.josh.indian-600.jpg',
    #                                   'name': ['testing name'],
    #                                   'quantity': ['1'],
    #                                   'measure': ['cup']},
    #                             follow_redirects=True)

    #     self.assertIn('<p> User Recipes: Total Number', result.data)
    #     self.assertEqual(result.status_code, 200)


    # def create_recipe(self):
    #     """ add new recipe using recipe form"""

    #     self.client.post('/')

    #     Recipe.create_recipe('testtitle', 3, userid, 'test preparation', 5, 'http://www.ndtv.com/cooks/images/rogan.josh.indian-600.jpg')

    # def load_recipe_data():
    #     """ adding new recipe to temp database"""

    #     Recipe.create_recipe("testtitle", 1, 1, "steps to prepare" , 2, image)

if __name__ == "__main__":
    unittest.main()

