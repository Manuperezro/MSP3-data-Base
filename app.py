from flask import Flask, render_template, request 
app = Flask(__name__)


@app.route('/')
def start():
    return render_template('base.html')


@app.route('/create-restaurant', methods=['GET', 'POST'])
def create_restaurant():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        site_url = request.form.get('site_url')

        return '{}, {}, {}'.format(name, description, site_url)
    return render_template('create_restaurant.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(debug=True)
