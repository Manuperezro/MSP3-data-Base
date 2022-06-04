from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
import os
import logging
from database import db_session, init_db
from sqlalchemy import desc
from models.recipes import Recipes
from models.User import Users
import MySQLdb.cursors
import datetime
import re
from werkzeug.security import generate_password_hash, check_password_hash
from random import choice
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

env_path = Path('.')/'.env'

load_dotenv(dotenv_path=env_path)

# Code isnpire with a few tutorials: 
# python CRUD udemy, Walktrhought project Code Institute, CRUD with Python codecademy.

# The app.logger.info("") = It is used for Debugin:
# I did log status of code to see if the code was working correctly it can be seeing in record.log

app = Flask(__name__)

# To dont storage any data 
app.config["SESSION_PERMANENT"] = True


# To store from the cookies. 
app.config["SESSION_TYPE"] = "filesystem"


Session(app)

# for  debuging 
logger = logging.getLogger()
logging.basicConfig(filename='record.log', level=logging.DEBUG)

logger.info('IN app.py')


@app.before_first_request
def init():
    init_db()
    

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def start():
    if not session.get('username'):
        return render_template('login.html')     
    now = datetime.datetime.now

    return render_template('start.html', nav='start', now=now)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Add Useres to the Users table"""
    errorRegister = " "
    
    if request.method == "POST":
        # Get the data from the useres imput field in the Register form
        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        userNameExists = bool(Users.query.filter_by(username=username).first())
        userEmailExists = bool(Users.query.filter_by(email=email).first())
        
        if userNameExists is False and userEmailExists is False:
            # to catch error email or username doesn't exist

            if len(username) > 0 and len(email) > 0 and len(password) > 0:
                # to catch error usrname, email or password empty
                # Get New Users and add and commit to the users session.
                emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                # Email regex used to create what is an acceptable email format.
                if re.fullmatch(emailRegex, email):
                    user = Users(username=username, password=password, email=email)
                    db_session.add(user)
                    db_session.commit()
                    return redirect('/')
                else:
                    errorRegister = "Please enter a valid Email"
                    return render_template('register.html', errorRegister=errorRegister)

            else:
                # to catch error username, email or password empty
                if len(username) == 0:
                    errorRegister = "Please enter a Username"
                elif len(email) == 0:
                    errorRegister = "Please enter an Email"
                elif len(password) == 0:
                    errorRegister = "Please enter a Password"    

                return render_template('register.html', errorRegister=errorRegister)
        else:
            if userNameExists:
                errorRegister = "Username is already in use"
            elif userEmailExists:
                errorRegister = "Email is already in use"
            
            return render_template('register.html', errorRegister=errorRegister)

    return render_template('register.html', errorRegister=errorRegister)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Users Session login"""
    errorMessage = " "

    if request.method == "POST":
        username = request.form.get('username')
        
        password = request.form.get('password')

        if len(username) > 0 and len(password) > 0:
            # Check if username is in the Users table.
            userExists = bool(Users.query.filter_by(username=username).first())

            # Get users by username 
            user = Users.query.filter(Users.username == username).first()

            if userExists is True:
                # Check if Users exists and if password match to the Users table data

                check_user_password = check_password_hash(user.password, password)
                if check_user_password:
                    session['username'] = user.username
                    session['password'] = user.password
                    session['userId'] = user.id
                    session['loggedIn'] = True
                    flash(f"Welcomeback, {session.get('username')}!")
                    return redirect('/') 
                    return render_template('start.html')
                else:
                    # Wrong password
                    errorMessage = "Invalid Password "
                    app.logger.info('errorMessage %s', errorMessage)
                    
            else:
                # account dosn't exist
                errorMessage = "Invalid Username or Password "
                
        else:
            if len(username) == 0:
                errorMessage = "Please enter a Username"
            elif len(password) == 0:
                errorMessage = "Please enter a Password"    
            return render_template('login.html', errorMessage=errorMessage)

        # When users favourite recipes store into users database. add this to the others routes.

    return render_template('login.html', errorMessage=errorMessage)

@app.route('/logout')
def logout():
    """Closed Useres session"""
    
    flash(f"You are logout! See you soon!")
    session.pop('username', None)
    session.pop('id', None)
    session.pop('loggedIn', None)

    return redirect('/register')

# Code inspire by a udemy flask video-tutorial LuckyDraw,
# What to cook buttom take a random recipe from The History list and siplay the link and name to the User 
@app.route('/draw')
def draw():
    """Take a random recipe from the History to help the User with the decision"""
    recipes = Recipes.query.all()

    if not recipes:
        return redirect('/create-recipe')

    random_recipe = choice(recipes)

    recipe = Recipes.query.get(random_recipe.id)
    recipe.draw += 1
    db_session.commit()

    now = datetime.datetime.now()

    return render_template('draw.html', recipe=recipe, now=now)


# Create a recipe and added to the User and History list
@app.route('/create-recipe', methods=['GET', 'POST'])
def create_recipe():
    """Create a nw recipy and added to both lists, History and My recipes list"""

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        site_url = request.form.get('site_url')
        user_id = session.get('userId')
        recipe = Recipes(name=name, description=description, site_url=site_url, user_id=user_id)
        db_session.add(recipe)
        db_session.commit()
    
        return redirect('/recipes')
    return render_template('create_recipe.html')


# The list of recipe
@app.route('/recipes')
def user_recipe_list():
    userId = session.get('userId')
    recipes = Recipes.query.filter(Recipes.user_id == userId).all()
    return render_template("recipe.html", nav=recipes, recipes=recipes)


# Edit the recipes from user list
@app.route('/edit-recipe', methods=['GET', 'POST'])
def edit_recipe():

    id = request.args.get('id')

    recipe = Recipes.query.filter(Recipes.id == id).first()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        site_url = request.form.get('site_url')
        recipe.name = name
        recipe.description = description
        recipe.site_url = site_url
        recipe.modified_time = datetime.datetime.now()
        
        db_session.commit()
        return redirect('/recipes')
    return render_template('edit_recipe.html', recipe=recipe)


# Delete recipes from users and History list
@app.route('/delete-recipe')
def delete_recipe():
    id = request.args.get('id')
    recipe = Recipes.query.filter(Recipes.id == id).first()

    if recipe:
        db_session.delete(recipe)
        db_session.commit()
    return redirect('/recipes')


# render template for History 
@app.route('/history')
def history():
    histories = Recipes.query.all()
    app.logger.info('histories are %s', histories)
    return render_template('history.html', nav=history, recipes=histories)


# Search recipes in the History list 
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['search_string']
        app.logger.info('search Value = %s', search_value)
        search = "%{}%".format(search_value)
        results = Recipes.query.filter(Recipes.name.like(search)).all()
        app.logger.info('Results = %s', results)
        return render_template('history.html', recipes=results, legend="Search Results")
    else:
        return redirect('history.html')


# Code inspire by a udemy flask video-tutorial LuckyDraw,
# To format the text depending on time. 
def mealformat(value):
    if value.hour in [4, 5, 6, 7, 8, 9]:
        return 'Breakfast'
    elif value.hour in [10, 11, 12, 13, 14, 15]:
        return 'Lunch'
    elif value.hour in [16, 17, 18, 19, 20, 21]:
        return 'Dinner'
    else:
        return 'Supper'


def datetimeformat(value):
    return value.strftime("%m/%d/%Y, %H:%M:%S")


app.jinja_env.filters['meal'] = mealformat
app.jinja_env.filters['datetime'] = datetimeformat


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)