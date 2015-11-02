"""Recipe Storage."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Recipe, Category, Ingredient

import datetime

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "secret key"

# Normally, if you use an undefined variable in jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def splash_page():
    """This is root route. Shows splash_page to the user with sign in and sign
    up button"""

    return render_template("splash_page.html")


@app.route('/signup', methods=['GET'])
def show_sign_up_form():
    """Show form for user sign up"""

    return render_template("signup_form.html")


@app.route('/signup-confirm', methods=['POST'])
def process_sign_up_form():
    """New user sign up process"""

    #Get sign up form variables
    username = request.form["username"]
    user_password = request.form["password"]
    user_email = request.form["email"]

    user_confirmed = User.get_user_via_email(user_email)

    if not user_confirmed:
        User.create_user(username, user_password, user_email)
        flash("Your account has been created successfully")
    else:
        flash("you already have an account, please sign in.")

    return redirect("/signin")


@app.route('/signin', methods=['GET'])
def show_sign_in_form():
    """Show sign in form"""

    return render_template("signin_form.html")


@app.route('/signin-confirm', methods=['POST'])
def process_sign_in_form():
    """Sign in process"""

    #get sign in form variables:
    username = request.form["username"]
    password = request.form["password"]

    print username, password

    user_confirmed = User.validate_username_and_password(username, password)

    print user_confirmed

    if user_confirmed:
        print "user_confirmed"
        userid = user_confirmed.user_id
        print userid
        session["user_id"] = userid
        print session["user_id"]
        url = "/recipeform"
        #url = "/myrecipe-list", session["user_id"]
        return redirect(url)
    else:
        flash("username and password combination are Incorrect.")
        return redirect("/signin")


@app.route('/logout')
def logout():
    """Log out"""

    del session["user_id"]
    flash("You are successfully Logged Out.")
    return redirect("/")


@app.route('/recipe-list', methods=['GET'])
def show_my_recipe():
    """Show interactive recide list page for a perticular user"""

    #query db to get users recipies 
    db_categories = Category.query.all()
    db_recipes = Recipe.query.all()
    db_ingredients = Ingredient.query.all()
    #jinja iterate over list of recipes

    return render_template("recipe_list.html", db_categories=db_categories, db_recipes=db_recipes, db_ingredients=db_ingredients)


@app.route('/recipeform', methods=['GET'])
def show_recipe_form():
    """show recipe form"""
    
    db_categories = Category.query.all()


    return render_template("recipe_form.html", db_categories=db_categories)


@app.route('/recipeform-confirm', methods=['POST'])
def process_recipe_form():
    """Process recipe form to add new recipe to the database."""
    # Get category id out of request.form and add to Recipe as category_id.

    #get recipe form variables
    # print request.form
    # print request.form["title"]
    # print request.form["preparation"]
    # print request.form["category_name"]
    # print request.form["ingredients.ingredients_name"]
    # print request.form["ingredients.measure"]
    # print request.form["ingredients.quantity"]

    # print session["user_id"]

    userid = session["user_id"]

    title = request.form["title"]
    preparation = request.form["preparation"]
    yields = request.form["yields"]
    #userid = request.form["user_id"]
    category_id = request.form["category_name"]
    #category_id = request.form["category_id"]
    
    # Get first ingredient

    qty1 = request.form["ingredients.quantity1"]
    measure1 = request.form["ingredients.measure1"]
    item1 = request.form["ingredients.ingredients_name1"]

    # Get second ingredeient
    qty2 = request.form["ingredients.quantity2"]
    measure2 = request.form["ingredients.measure2"]
    item2 = request.form["ingredients.ingredients_name2"]


    # Get third ingredient
    qty3 = request.form["ingredients.quantity3"]
    measure3 = request.form["ingredients.measure3"]
    item3 = request.form["ingredients.ingredients_name3"]

    # category_id = Category.get_category_id(category_name)
    # print category
    # print category
    # print category
    # print category


    recipe_id = Recipe.create_recipe(title, category_id, userid, preparation, yields)

    # Make first ingredient
    ing1 = Ingredient.create_ingredient(quantity=qty1, measure=measure1, item=item1, recipe_id=recipe_id)
    # Make second ingredeitn
    ing2 = Ingredient.create_ingredient(quantity=qty2, measure=measure2, item=item2, recipe_id=recipe_id)
    # Make third ing.
    ing3 = Ingredient.create_ingredient(quantity=qty3, measure=measure3, item=item3, recipe_id=recipe_id)

    # Category.get_category_name(category_name)

    # #to do
    # #add ingredient to database dynamically
    # #get ingredient from recipe form dynamically

    return redirect("/recipe-list")


@app.route('/edit-recipe', methods=['GET'])
def show_prefilled_recipe_form():
    """Show existing prefilled recipe form"""

    return render_template("/recipe_form.html")


@app.route('/edit-recipe', methods=['POST'])
def process_edit_on_recipe_form(recipe_id):
    """Allows user to edit existing recipe and Save"""

    #use jinja,  Recipe List {%for recipe in recipes%}
    #<a href ="/editrecipe(route)/{{recipe_id}}"
    # EDIT (button) </a>
    # @app.route("/editrecipe/<int: recipe_id>")
    # def process_edit(recipe_id)
    # get recipe out of DB
    # return form with prefilled values

    return redirect("/recipe-list")


@app.route('/view-recipe', methods=['GET'])
def show_view_recipe_page():
    """Show view recipe page"""

    return render_template("view_recipe.html")


if __name__ == "__main__":
    # Set debug=True, since it has to be True at the point that we invoke the
    # DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    #Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
