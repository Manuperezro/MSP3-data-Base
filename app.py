from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
import os 
import logging
from database import db_session, init_db
from sqlalchemy import desc
from models.recipes import Recipes
from models.histories import Histories 
from models.register import Users
import MySQLdb.cursors
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from random import choice


# Code isnpire with a few tutorials: 
# python CRUD udemy, Walktrhought project Code Institute, CRUD with Python codecademy.
# the app.logger.info("") = It is used for Debugin:
# I did log status of code to see if the code was working correctly it can be seeing in record.log

app = Flask(__name__)


app.secret_key = os.environ.get("SECRET_KEY")


# To dont storage any data 
app.config["SESSION_PERMANENT"] = False


# To store from the cookies. 
app.config["SESSION_TYPE"] = "filesystem"


Session(app)


app.logger.info('IN app.py')
app.logger.info('app.config', app.config)

# for  debuging 

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


@app.before_first_request
def init():
    init_db()
    

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def start():
    app.logger.info('IN START')
    if not session.get('username'):
        return render_template('login.html')     
    now = datetime.datetime.now
    app.logger.info('Session username', session.get('username'))
    app.logger.info('Leged In', session.get('loggedIn'))
    return render_template('start.html', nav='start', now=now)


@app.route('/register', methods=['GET', 'POST'])
def register():

    app.logger.info('register-route')
    
    if request.method == "POST" and "username" in request.form and "email" in request.form and "password" in request.form:
        # check if username already exist
        app.logger.info('impost request')
        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        app.logger.info('username are %s', username)
        app.logger.info('password are %s', password)

        user = Users(username=username, email=email, password=password)
        db_session.add(user)
        db_session.commit()

        return redirect('/login')

    return render_template('register.html')


# @app.route('/userslog')
# def userslog():
#     userslog = Users.query.all()
#     return render_template('users.html', userslog=userslog)


@app.route('/login', methods=['GET', 'POST'])
def login():
    errorMessage = " "
    app.logger.info('in login function')
    app.logger.info('request ok', request.method)
    app.logger.info('request form,', request.form)
    if request.method == "POST" and "username" in request.form and "password" in request.form:
        #   account exists
        userslog = Users.query.all()
        app.logger.info('userlist is %s', userslog)

        username = request.form.get('username')
        app.logger.info('username ok %s', username)

        password = generate_password_hash(request.form.get('password'))
        app.logger.info('password ok %s', password)


        # check if user exists in register database
        userExists = bool(Users.query.filter_by(username=username).first())
        app.logger.info('user in  ok %s', userExists)
        if userExists is True:
            # get the user from the database
            user = Users.query.filter(Users.username == username and Users.password == password).first()
            session['username'] = user.username
            session['id'] = user.id
            session['loggedIn'] = True
            flash("Welcomeback, {user.username}!")

            return redirect('/') 
            return render_template('start.html')

        else:
            # account dosn't exist
            errorMessage = "Invalid Username or Password "

        # When users favourite recipes store into users database. add this to the others routes.


    return render_template('login.html', errorMessage=errorMessage)



@app.route('/logout')
def logout():

    flash("You are logout! See you soon!")
    session.pop('username', None)
    session.pop('id', None)
    session.pop('loggedIn', None)

    return redirect('/register')



# Try luck Buttom
@app.route('/draw')
def draw():
    recipes = Recipes.query.all()

    if not recipes:
        return redirect('/create-recipe')

    random_recipe = choice(recipes)

    recipe = Recipes.query.get(random_recipe.id)
    # recipe.draw += 1
    db_session.commit()

    now = datetime.datetime.now()

    return render_template('draw.html', recipe=recipe, now=now)


@app.route('/create-recipe', methods=['GET', 'POST'])
def create_recipe():

    app.logger.info('CREATE RECIPE %s')
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        site_url = request.form.get('site_url')
        username = request.form.get('username')

        user = Users.query.filter(Users.username == username).first()
        app.logger.info('user in create %s', user)


        recipe = Recipes(name=name, description=description, site_url=site_url)

        # app.logger.info('recipe ==  %s', recipe.id)

        # user.recipe_ids.append(recipe.id)

        # addRecipe = user.recipe_ids.append(recipe.id)

        # db_session.add(addRecipe)

        db_session.add(recipe)
        db_session.commit()

        # app.logger.info('is recipe addded to user ?  %s', user.recipe_ids)
        return redirect('/recipes')


    return render_template('create_recipe.html')


@app.route('/recipes')
def recipe_list():
    recipes = Recipes.query.all()

    return render_template("recipe.html", nav=recipes, recipes=recipes)


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


@app.route('/delete-recipe')
def delete_recipe():

    id = request.args.get('id')

    recipe = Recipes.query.filter(Recipes.id == id).first()

    if recipe:
        db_session.delete(recipe)
        db_session.commit()

    return redirect('/recipes')


@app.route('/history')
def history():

    histories = Recipes.query.all()
    app.logger.info('histories are %s', histories)

    return render_template('history.html', nav=history, recipes=histories)


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


# Code inspire by a udemy flask video-tutorial,
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