from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def start():
    return render_template('base.html')


@app.route('/create-restaurant')
def create_restaurant():
    return render_template('create_restaurant.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)
