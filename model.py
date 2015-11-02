"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import datetime

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_user_via_email(cls, user_email):
        """check if an account with a given email address is already exists."""

        try:
            login_info = cls.query.filter_by(email=user_email).one()
            return login_info

        except Exception, error:
            print error

    @classmethod
    def create_user(cls, username, user_password, user_email):
        """ Add a new user info to the database"""

        new_user = User(username=username, password=user_password, email=user_email)

        db.session.add(new_user)
        db.session.commit()

        return new_user

    @classmethod
    def validate_username_and_password(cls, username, user_password):
        """ check user entered email and password are correct"""

        try:
            login_info = cls.query.filter_by(username=username, password=user_password).one()
            return login_info

        except Exception, error:
            print error

    def __repr__(self):
        """Make printing the object useful"""

        repr_string = ("<User user_id: {user_id}, username: {user_name}, " +
                       "password: {password}, email: {email},")

        return repr_string.format(user_id=self.user_id,
                                  user_name=self.username,
                                  password=self.password,
                                  email=self.email)


class Recipe(db.Model):

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, nullable=False, autoincrement=True,
                          primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"),
                            nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey("users.user_id"),
                        nullable=False)
    preparation = db.Column(db.Text, nullable=False)
    yields = db.Column(db.Integer, nullable=False)
    #created_at = db.Column(db.DateTime, nullable=False,
     #                      default="CURRENT_TIMESTAMP")
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.utcnow())

    @classmethod
    def create_recipe(cls, title=title, category_id=category_id, user_id=user_id, preparation=preparation, yields=yields):
        """Add a new recipe to the database."""
        print "THIS FUNCTION GET CALLED MY POST"

        new_recipe = Recipe(title=title,
                            category_id=category_id,
                            user_id=user_id,
                            preparation=preparation,
                            yields=yields)

        db.session.add(new_recipe)
        db.session.commit()

        recipe = Recipe.query.filter_by(title=title, user_id=user_id).first()
        return recipe.recipe_id

    def __repr__(self):
        """Make printing the object useful"""

        repr_string = ("<Recipe recipe_id: {recipe_id}, title: {title}," +
                       "category_id: {category_id}, total_time: {total_time}" +
                       "preparation: {preparation}, user_id: {user_id}," +
                       "yields: {yields}, created_at: {created_at}>")

        return repr_string.format(recipe_id=self.recipe_id,
                                  title=self.title,
                                  category_id=self.category_id,
                                  preparation=self.preparation,
                                  user_id=self.user_id,
                                  yields=self.yields,
                                  created_at=self.created_at)


class Category(db.Model):

    __tablename__ = "categories"

    category_id = db.Column(db.Integer, nullable=False, autoincrement=True,
                            primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)

    @classmethod
    def get_category_name(cls, category_name):
        """get user selected category name and add it to database"""

        category_name = Category(category_name=category_name)

        db.session.add(category_name)
        db.session.commit()
        return category_name

    @classmethod
    def get_category_id(cls, category_name):
        """get category id"""

        category = Category.query.filter_by(category_name=category_name).first()

        return category.category_id

    def __repr__(self):
        """Make printing the object useful"""

        repr_string = ("<Category category_id: {category_id}," +
                       "category_name: {category_name},")

        return repr_string.format(category_id=self.category_id,
                                  category_name=self.category_name)


class Ingredient(db.Model):

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, nullable=False, autoincrement=True,
                              primary_key=True)
    ingredient_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    measure = db.Column(db.Integer, nullable=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.recipe_id"))

    @classmethod
    def create_ingredient(cls, quantity, measure, item, recipe_id):
        """get ingredient and store in db"""

        new_ingredient = Ingredient(ingredient_name=item,
                                    quantity=quantity,
                                    measure=measure,
                                    recipe_id=recipe_id)

        db.session.add(new_ingredient)
        db.session.commit()

        return new_ingredient



    def __repr__(self):
        """Make printing the object useful"""

        repr_string = ("<Ingredient ingredient_id: {ingredient_id}," +
                       "ingredient_name: {ingredients_name}" +
                       "quantity: {quantity}, measure: {measure}" +
                       "recipe_id: {recipe_id}>")

        return repr_string.format(ingredient_id=self.ingredient_id,
                                  ingredient_name=self.ingredient_name,
                                  quantity=self.quantity,
                                  measure=self.measure,
                                  recipe_id=self.recipe_id)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to the Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipedb.db'

    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if i run this module interactively, it will leave
    # me in a state of being able to work with the database directly.
    from server import app
    connect_to_db(app)
    print "Connected to DB."
