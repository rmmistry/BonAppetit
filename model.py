"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import datetime

# This is the connection to the SQLite database; I am getting this through
# the Flask-SQLAlchemy helper library. On this, I can find the `session`
# object, where I do most of my interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    yummly_recipes = db.relationship("Yummlyrecipe", secondary="yummlyusers", backref="users")

    @classmethod
    def get_user_via_email(cls, user_email):
        """check if an account with a given email address is already exists."""

        login_info = cls.query.filter_by(email=user_email).first()
        return login_info

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
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.utcnow())
    image = db.Column(db.String(255), nullable=True)
    category = db.relationship("Category", backref=db.backref("recipes"))

    @classmethod
    def create_recipe(cls, title=title, category_id=category_id, user_id=user_id, preparation=preparation, yields=yields, image=image):
        """Add a new recipe to the database."""
        print "THIS FUNCTION GET CALLED BY POST"

        new_recipe = Recipe(title=title,
                            category_id=category_id,
                            user_id=user_id,
                            preparation=preparation,
                            yields=yields,
                            image=image)

        db.session.add(new_recipe)
        db.session.commit()
        return new_recipe

    @classmethod
    def get_recipe_id(cls, title, user_id):
        """finds recipeid for a given title and userid"""

        recipe = Recipe.query.filter_by(title=title, user_id=user_id).first()
        return recipe.recipe_id

    @classmethod
    def get_existing_recipe(cls, recipeid):
        """get existing recipe for a given recipeid"""

        recipe = Recipe.query.get(recipeid)
        return recipe

    @classmethod
    def delete_existing_recipe(cls, recipeid):
        """allows user to delete existing recipe"""

        delete_recipe = Recipe.query.filter_by(recipe_id=recipeid).delete()

        db.session.commit()
        return delete_recipe

    def __repr__(self):
        """Make printing the object useful"""

        repr_string = ("<Recipe recipe_id: {recipe_id}, title: {title}," +
                       "category_id: {category_id}," +
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
    ingredient_name = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    measure = db.Column(db.String(255), nullable=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.recipe_id"))

    @classmethod
    def create_ingredient(cls, item, quantity, measure, recipe_id):
        """get ingredient and store in db"""

        new_ingredient = Ingredient(ingredient_name=item,
                                    quantity=quantity,
                                    measure=measure,
                                    recipe_id=recipe_id)

        db.session.add(new_ingredient)
        db.session.commit()

        return new_ingredient

    @classmethod
    def get_existing_ingredients(cls, recipeid):
        """get a list of ingredients in a given recipeid """

        existing_ingredients = Ingredient.query.filter_by(recipe_id=recipeid).all()
        return existing_ingredients

    @classmethod
    def delete_existing_ingredients(cls, recipeid):
        """allows user to delete existing recipe"""

        delete_ingredient = Ingredient.query.filter_by(recipe_id=recipeid).delete()

        db.session.commit()
        return delete_ingredient

    def __repr__(self):
        """Make printing the object useful"""

        repr_string = ("<Ingredient ingredient_id: {ingredient_id}," +
                       "ingredient_name: {ingredient_name}" +
                       "quantity: {quantity}, measure: {measure}" +
                       "recipe_id: {recipe_id}>")

        return repr_string.format(ingredient_id=self.ingredient_id,
                                  ingredient_name=self.ingredient_name,
                                  quantity=self.quantity,
                                  measure=self.measure,
                                  recipe_id=self.recipe_id)


class Yummlyrecipe(db.Model):

    __tablename__ = "yummlyrecipes"

    yummly_recipe_id = db.Column(db.String(300), primary_key=True, unique=True, nullable=False)
    searched_title = db.Column(db.String(255), nullable=False)
    prep_url = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        """Make printing the object useful"""

        repr_string = ("<Yummlyrecipe yummly_recipe_id: {yummly_recipe_id}," +
                       "searched_title: {searched_title}," +
                       "prep_url: {prep_url}," +
                       "image_url: {image_url}>")

        return repr_string.format(yummly_recipe_id=self.yummly_recipe_id,
                                  searched_title=self.searched_title,
                                  prep_url=self.prep_url,
                                  image_url=self.image_url)

    @classmethod
    def create_api_recipe(cls, yummly_recipe_id=yummly_recipe_id, searched_title=searched_title, prep_url=prep_url, image_url=image_url):
        """Add a new recipe from api to the database."""

        new_api_recipe = Yummlyrecipe(yummly_recipe_id=yummly_recipe_id,
                                      searched_title=searched_title,
                                      prep_url=prep_url,
                                      image_url=image_url)

        db.session.add(new_api_recipe)
        db.session.commit()
        return new_api_recipe

    @classmethod
    def delete_existing_yummly_recipe(cls, yummly_recipe_id):
        """allows user to delete existing yummly recipe"""

        delete_yummly_recipe = Yummlyrecipe.query.filter_by(yummly_recipe_id=yummly_recipe_id).delete()
        db.session.commit()
        return delete_yummly_recipe


class Yummlyuser(db.Model):

    __tablename__ = "yummlyusers"

    yummly_id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    yummly_recipe_id = db.Column(db.String, db.ForeignKey("yummlyrecipes.yummly_recipe_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    def __repr__(self):
        """Make printing the object useful"""

        repr_string = ("<yummlyusers yummly_id: {yummly_id}," +
                       "yummly_recipe_id: {yummly_recipe_id}," +
                       "user_id: {user_id}>")

        return repr_string.format(yummly_id=self.yummly_id,
                                  yummly_recipe_id=self.yummly_recipe_id,
                                  user_id=self.user_id)

    @classmethod
    def create_yummly_user(cls, yummly_recipe_id=yummly_recipe_id, user_id=user_id):
        """Add a yummly user to DB"""

        yummly_user = Yummlyuser(yummly_recipe_id=yummly_recipe_id, user_id=user_id)

        db.session.add(yummly_user)
        db.session.commit()
        return yummly_user

##############################################################################
# Helper functions


def connect_to_db(app, db_uri="sqlite:///recipedb.db"):
    """Connect the database to the Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # As a convenience, if i run this module interactively, it will leave
    # me in a state of being able to work with the database directly.
    from server import app
    connect_to_db(app)
    print "Connected to DB."
