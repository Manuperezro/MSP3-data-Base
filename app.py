from flask import Flask, render_template, request, redirect
import os 
import logging
import flask_login
from database import db_session, init_db
from sqlalchemy import desc
from models.recipes import Recipes
from models.histories import Histories 
from models.register import Users
import datetime
from random import choice
from flask import session


app = Flask(__name__)

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
    now = datetime.datetime.now
    return render_template('start.html', nav='start', now=now)


@app.route('/register', methods=['GET', 'POST'])
def register():

    app.logger.info('register-route')
    
    if request.method == 'POST':
        app.logger.info('impost request')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        app.logger.info('username are %s', username)
        app.logger.info('password are %s', password)

        user = Users(username=username, email=email, password=password)
        db_session.add(user)
        db_session.commit()

        return redirect('/register')


    return render_template('register.html')


@app.route('/userslog')
def userslog():
    userslog = Users.query.all()
    return render_template('users.html', userslog=userslog)


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    # check if username exist in db (Look for an single user in Users table)
    return render_template('login.html')


# @app.route('logout')
# def logout():
#     return redirect('/login')


@app.route('/draw')
def draw():
    recipes = Recipes.query.all()

    if not recipes:
        return redirect('/create-recipe')

    random_recipe = choice(recipes)

    recipe = Recipes.query.get(random_recipe.id)
    recipe.draw += 1
    db_session.commit()

    now = datetime.datetime.now()

    return render_template('draw.html', recipe=recipe, now=now)


@app.route('/create-recipe', methods=['GET', 'POST'])
def create_recipe():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        site_url = request.form.get('site_url')

        recipe = Recipes(name=name, description=description, site_url=site_url)
        db_session.add(recipe)
        db_session.commit()

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