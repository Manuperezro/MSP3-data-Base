from flask import Flask, render_template, request 
from database import db_session, init_db
from models.restaurants import Restaurants
app = Flask(__name__)


# before the first request is send, initialize the database
@app.before_first_request
def init():
    init_db()


# to clean the page after all the request are done move the databa sesesion
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def start():
    return render_template('base.html')


@app.route('/create-restaurant', methods=['GET', 'POST'])
def create_restaurant():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        site_url = request.form.get('site_url')

        restaurant = Restaurants(name=name, description=description, site_url=site_url,)
        db_session.add(restaurant)
        db_session.commit()

        return '{}, {}, {}'.format(name, description, site_url)

    return render_template('create_restaurant.html')


@app.route('/restaurants')
def restaurant_list():
    restaurants = Restaurants.query.all()
    return render_template("restaurant.html", restaurants=restaurants)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)
