"""Recipe Storage."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Recipe, Category, Ingredient, Yummlyrecipe, Yummlyuser

import datetime

import requests
import json
import os

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "secret key"

# Normally, if you use an undefined variable in jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined
#setting API key
APP_ID=os.environ.get("APP_ID")
APP_SECRET_KEY=os.environ.get("APP_KEY")


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

    user_id=session.get("user_id")

    if user_id:
        print "\n\n\n%s\n\n\n"%user_id
        user = User.query.get(int(user_id))
        #query db to get users recipies
        db_categories = Category.query.all()
        db_recipes = Recipe.query.filter_by(user_id=user_id).all()
        db_ingredients = Ingredient.query.all()
        # yummlyusers = Yummlyuser.query.filter_by(user_id=user_id).all()
        # yummlyrecipes = Yummlyrecipe.query.filter_by(yummly_recipe_id=yummly_recipe_id).all()
        
        yummly_info = []
        for recipe in user.yummly_recipes:
            yummly_info.append(recipe)


        print yummly_info

        #jinja iterates over list of recipes, categories and ingredients to get title, Category, Date added info to show on recipe list
        return render_template("recipe_list.html", user=user, db_recipes=db_recipes, db_categories=db_categories, db_ingredients=db_ingredients, yummly_info=yummly_info)
    else:
        return redirect("/signin")


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
    print preparation
    yields = request.form["yields"]
    category_id = request.form["category_name"]
    image = request.form["image"]

    ingredient_names = request.form.getlist('name')
    ingredient_quantities = request.form.getlist('quantity')
    ingredient_measures = request.form.getlist('measure')

    print "INGREDIENT NAME: ", ingredient_names
   
    #recipe_id = Recipe.create_recipe(title, category_id, userid, preparation, yields)
    Recipe.create_recipe(title, category_id, userid, preparation, yields, image)

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
    print recipe.image

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
    recipe.image = request.form["image"]

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

###################################################################################

@app.route("/recipes/<int:recipeid>", methods=['GET'])
def delete_recipe(recipeid):
    """deletes recipe for a given recipeid from database"""

    #Delete recipe when user clicks on a remove icon
    Recipe.delete_existing_recipe(recipeid)

    flash("Your recipe has been deleted successfully")  
    return redirect("/recipe-list")


@app.route('/view-recipe/<int:recipeid>', methods=['GET'])
def show_view_recipe_page(recipeid):
    """Show view recipe page"""

    recipe = Recipe.get_existing_recipe(recipeid)
    ingredients = Ingredient.get_existing_ingredients(recipeid)



    #return str(recipeid)
    return render_template("/display_recipe.html", recipe_id=recipeid, recipe=recipe, ingredients=ingredients)

    #url_for('show_view_recipe_page', recipeid=recipe.recipe_id, _external=True)}}
    #when user clicks on a share link - model window should pop up and that model window should get this above link.
######################################################################################

@app.route('/api', methods=['POST'])
def recipe_api():

    print "got here"
    query = request.form["searchbox"]
    print "query: ", query
 
    #r = requests.get("https://api.edamam.com/search?q=" + query + "&app_id=" + APP_ID + "&app_key=" + APP_SECRET_KEY)
    # print "http://api.yummly.com/v1/api/recipes?_app_id="+ APP_ID +"&_app_key="+ APP_SECRET_KEY +"&"+ query

    r = requests.get("http://api.yummly.com/v1/api/recipes?_app_id="+ APP_ID +"&_app_key="+ APP_SECRET_KEY + "&q=" + query)
    results = r.json() #is this json and if it is then it turns type to dictionary

    # key =results.keys() # list
    # print key

    values = results['matches']# dictionary
    # print "values: ", values# list

    # recipe_search_id=[]
    # recipe_search_title=[]

    recipe_display={}

    for i in range(len(values)):
        recipe_id = values[i]['id']
        splitted_list = recipe_id.split("-")
        print splitted_list
        title = splitted_list[0:-1]
        print title
        full_title = " ".join(title)
        print full_title
        recipe_display[full_title]=recipe_id
        # recipe_search_title.append(full_title)
        # recipe_search_id.append(recipe_id)
        print "recipe id: ", recipe_id


    return render_template("recipe_search_results.html", recipe_display=recipe_display)


@app.route('/display/<string:recipe_id>')
def get_recipe_info_by_id(recipe_id):
    """ gets recipe info for a given id"""

    r = requests.get("http://api.yummly.com/v1/api/recipe/" + recipe_id + "?_app_key=" + APP_SECRET_KEY + "&_app_id=" + APP_ID)
    results = r.json()

    required_info = {}
    print required_info

    for i in results:
        title1 = results['name']
        ingredients = results['ingredientLines']
        yields = results['yield']
        # prep_time = results['prepTime']
        prep_time = results.get('prepTime', 'not defined')
        cook_time = results.get('cookTime', 'not defined')
        rating = results.get('rating', 'not defined')
        total_time = results['totalTime']
        url = results['images'][0]['hostedMediumUrl']
        source_url = results['source']['sourceRecipeUrl']
        
        required_info[title1] = {'ingredients': ingredients,
                                 'yields': yields,
                                 'prep_time': prep_time,
                                 'cook_time': cook_time,
                                 'rating': rating,
                                 'total_time': total_time,
                                 'url': url,
                                 'source_url': source_url,
                                 'recipe_id': recipe_id
                                 }
    print "required_info : ", required_info

    recipe_exist_db = Yummlyuser.query.filter_by(yummly_recipe_id=recipe_id, user_id=session["user_id"]).first()
    print "SEARCH RESULT", recipe_exist_db
    # obj = jsonify(required_info)
    return render_template("searched_recipe_display.html", required_info=required_info, recipe_exist_db=recipe_exist_db)

@app.route('/api-recipe/<string:recipe_id>', methods=['POST'])
def process_api_recipe(recipe_id):
    """add API recipe info into DB"""

    yummly_recipe_id = request.form["api_recipe_id"]
    searched_title = request.form["api_recipe_title"]
    prep_url = request.form["source_url"]
    image_url = request.form["img_url"]
    user_id = session.get("user_id")

    # check if this recipe is in Yummlyrecipe table
    recipe_exist = Yummlyrecipe.query.filter_by(yummly_recipe_id=yummly_recipe_id).first()
    print recipe_exist
    if recipe_exist is None:
        Yummlyrecipe.create_api_recipe(yummly_recipe_id, searched_title, prep_url, image_url)
        print "THIS IS WORKING"
    user_recipe_exist = Yummlyuser.query.filter_by(yummly_recipe_id=yummly_recipe_id, user_id=user_id).first()
    if user_recipe_exist is None:
        Yummlyuser.create_yummly_user(yummly_recipe_id, user_id)

    return redirect("/recipe-list")

@app.route("/remove-apirecipes/<string:recipe_id>", methods=['GET'])
def delete_api_recipe(recipe_id):
    """deletes API recipe for a given recipeid from database"""

    #Delete recipe when user clicks on a remove icon
    Yummlyrecipe.delete_existing_yummly_recipe(recipe_id)

    flash("Your recipe has been deleted successfully")  
    return redirect("/recipe-list")

@app.route("/calculate-quantity/")
def quantity(yields):

    pass




if __name__ == "__main__":
    # Set debug=True, since it has to be True at the point that we invoke the
    # DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    #Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
