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
    """Show interactive recipe list page for a perticular user"""

    #query db to get users recipies
    db_categories = Category.query.all()
    db_recipes = Recipe.query.all()
    db_ingredients = Ingredient.query.all()

    #jinja iterates over list of recipes, categories and ingredients to get title, Category, Date added info to show on recipe list
    return render_template("recipe_list.html", db_recipes=db_recipes, db_categories=db_categories, db_ingredients=db_ingredients)


@app.route('/recipeform', methods=['GET'])
def show_recipe_form():
    """show recipe form"""

    db_categories = Category.query.all()
    print db_categories

    return render_template("recipe_form.html", db_categories=db_categories)


@app.route('/recipeform-confirm', methods=['POST'])
def process_recipe_form():
    """Process recipe form to add new recipe to the database."""
    
    #get recipe form variables
    print "request.form: ", request.form

    userid = session["user_id"]
    title = request.form["title"]
    preparation = request.form["preparation"]
    yields = request.form["yields"]
    category_id = request.form["category_name"]

    ingredient_names = request.form.getlist('name')
    ingredient_quantities = request.form.getlist('quantity')
    ingredient_measures = request.form.getlist('measure')

    print "INGREDIENT NAME: ", ingredient_names
   
    #recipe_id = Recipe.create_recipe(title, category_id, userid, preparation, yields)
    Recipe.create_recipe(title, category_id, userid, preparation, yields)

    recipe_id = Recipe.get_recipe_id(title, userid)

    for i in range(len(ingredient_names)):
        item = ingredient_names[i]
        quantity = ingredient_quantities[i]
        measure = ingredient_measures[i]
        Ingredient.create_ingredient(item=item, quantity=quantity, measure=measure, recipe_id=recipe_id)

    return redirect("/recipe-list")

#########################################################################

@app.route("/recipes/<int:recipeid>/edit", methods=['GET'])
def show_prefilled_recipe_form(recipeid):
    """Show existing prefilled recipe form"""

    # recipe object
    recipe = Recipe.get_existing_recipe(recipeid)
    db_categories = Category.query.all()
    ingredients = Ingredient.get_existing_ingredients(recipeid)

    print "RECIPE OBJECT:", recipe
    print recipe.preparation

    return render_template("/edit_recipe_form.html", recipe=recipe, db_categories=db_categories, ingredients=ingredients)


@app.route("/edit-recipe/<int:recipeid>/confirm", methods=['POST'])
def process_confirm_recipe_edit(recipeid):
    """Allows user to edit existing recipe and Save"""

    #get recipe object using recipeid
    recipe = Recipe.get_existing_recipe(recipeid)
    #ger recipe object = request.form(name)
    recipe.recipe_id = recipeid
    recipe.title = request.form["title"]
    recipe.preparation = request.form["preparation"]
    recipe.yields = request.form["yields"]
    recipe.category_id = request.form["category_name"]

    recipe.ingredients = []

    ingredient_names = request.form.getlist('name')
    ingredient_quantities = request.form.getlist('quantity')
    ingredient_measures = request.form.getlist('measure')


    for i in range(len(ingredient_names)):
        item = ingredient_names[i]
        quantity = ingredient_quantities[i]
        measure = ingredient_measures[i]
        Ingredient.create_ingredient(item=item, quantity=quantity, measure=measure, recipe_id=recipeid)


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