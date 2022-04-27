from flask import Flask, render_template, request, redirect
import logging
from database import db_session, init_db
from sqlalchemy import desc
from models.recipes import Recipes
from models.histories import Histories 
import datetime
from random import choice


app = Flask(__name__)

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


@app.route('/draw')
def draw():
    recipes = Recipes.query.all()

    if not recipes:
        return redirect('/create-recipe')

    random_recipe = choice(recipes)

    try:
        recipe = recipes.query.get(random_recipe.id)
        recipe.draw += 1

        history = Histories(recipe_id=recipe.id)

        db_session.add(history)
        db_session.commit()

    except:
        db_session.rollback()
        return redirect('/')

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

    app.loger.infor('recipe =  %s', recipe)
    app.logger.info(' conunter = %s ', recipe.site_visits)
    
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
    app.logger.info('%s is = ', id)

    recipe = Recipes.query.filter(Recipes.id == id).first()
    app.logger.info('%s is = ', recipe)

    if recipe:
        app.logger.info('got recipe')
        db_session.delete(recipe)
        db_session.commit()

    return redirect('/recipes')


# @app.route('/visit-site')
# def visit_site():

#     id = request.args.get('id')
#     recipe = 
    





@app.route('/history')
def history():

    histories = Histories.query.order_by(desc(Histories.created_time)).limit(20)

    return render_template('history.html', nav=history, histories=histories)


@app.route('/top')
def top():
    recipes = Recipes.query.order_by('-draw').limit(5)

    return render_template('top.html', nav='top', recipes=recipes)


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
    app.run(debug=True)